from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


LEVEL_PRIORITY = {
    "green": 0,
    "yellow": 1,
    "orange": 2,
    "red": 3,
}


@dataclass(frozen=True)
class SecurityEvent:
    event_type: str
    level: str
    title: str
    instruction: str
    confidence: float
    location: str
    related_track_ids: list[int] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "level": self.level,
            "title": self.title,
            "instruction": self.instruction,
            "confidence": self.confidence,
            "location": self.location,
            "related_track_ids": list(self.related_track_ids),
            "evidence": dict(self.evidence),
            "timestamp": self.timestamp,
        }


def copy_security_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return deepcopy(events)


def select_highest_security_event(
    events: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if not events:
        return None
    return max(
        events,
        key=lambda event: (
            LEVEL_PRIORITY.get(str(event.get("level", "green")).lower(), 0),
            1 if event.get("event_type") == "HIGH_RISK_COMBINED" else 0,
        ),
    )


class SecurityRulesEngine:
    def __init__(
        self,
        rules_enabled: bool = True,
        normal_start_hour: int = 6,
        normal_end_hour: int = 22,
        crowding_person_threshold: int = 4,
        loiter_seconds: float = 15.0,
        event_cooldown_seconds: float = 10.0,
        high_risk_cooldown_seconds: float = 5.0,
        location: str = "KUET Main Gate",
        gate_zone_enabled: bool = False,
        gate_zone_x1: float = 0.15,
        gate_zone_y1: float = 0.20,
        gate_zone_x2: float = 0.85,
        gate_zone_y2: float = 1.00,
    ):
        self.rules_enabled = rules_enabled
        self.normal_start_hour = self._hour(normal_start_hour)
        self.normal_end_hour = self._hour(normal_end_hour)
        self.crowding_person_threshold = max(1, int(crowding_person_threshold))
        self.loiter_seconds = max(0.0, float(loiter_seconds))
        self.event_cooldown_seconds = max(0.0, float(event_cooldown_seconds))
        self.high_risk_cooldown_seconds = max(0.0, float(high_risk_cooldown_seconds))
        self.location = location
        self.gate_zone_enabled = bool(gate_zone_enabled)
        self.gate_zone_x1 = float(gate_zone_x1)
        self.gate_zone_y1 = float(gate_zone_y1)
        self.gate_zone_x2 = float(gate_zone_x2)
        self.gate_zone_y2 = float(gate_zone_y2)
        self._last_emitted_at: dict[str, datetime] = {}
        self._last_current_events: list[dict[str, Any]] = []

    @staticmethod
    def _hour(value: int) -> int:
        return max(0, min(23, int(value)))

    @staticmethod
    def _now(now: datetime | None = None) -> datetime:
        if now is None:
            return datetime.now().astimezone()
        if now.tzinfo is None:
            return now.astimezone()
        return now

    @staticmethod
    def _int(value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _float(value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _track_ids(tracks: list[dict[str, Any]]) -> list[int]:
        ids: list[int] = []
        for track in tracks:
            try:
                ids.append(int(track["track_id"]))
            except (KeyError, TypeError, ValueError):
                continue
        return ids

    def _is_after_hours(self, now: datetime) -> bool:
        hour = now.hour
        start = self.normal_start_hour
        end = self.normal_end_hour
        if start == end:
            return False
        if start < end:
            return not (start <= hour < end)
        return not (hour >= start or hour < end)

    def _cooldown_seconds_for(self, event_type: str) -> float:
        if event_type == "HIGH_RISK_COMBINED":
            return self.high_risk_cooldown_seconds
        if event_type == "NORMAL_ACTIVITY":
            return 0.0
        return self.event_cooldown_seconds

    def _passes_cooldown(self, event_type: str, now: datetime) -> bool:
        cooldown = self._cooldown_seconds_for(event_type)
        if cooldown <= 0:
            return True
        last_emitted = self._last_emitted_at.get(event_type)
        if last_emitted is None:
            return True
        return (now - last_emitted).total_seconds() >= cooldown

    def reset_cooldowns(self) -> None:
        self._last_emitted_at.clear()

    def get_cooldowns(self, now: datetime | None = None) -> dict[str, dict[str, Any]]:
        current_time = self._now(now)
        cooldowns: dict[str, dict[str, Any]] = {}
        for event_type, last_emitted in self._last_emitted_at.items():
            cooldown = self._cooldown_seconds_for(event_type)
            elapsed = max(0.0, (current_time - last_emitted).total_seconds())
            cooldowns[event_type] = {
                "last_emitted_at": last_emitted.isoformat(),
                "cooldown_seconds": cooldown,
                "remaining_seconds": round(max(0.0, cooldown - elapsed), 2),
            }
        return cooldowns

    def get_config(self) -> dict[str, Any]:
        return {
            "normal_start_hour": self.normal_start_hour,
            "normal_end_hour": self.normal_end_hour,
            "crowding_person_threshold": self.crowding_person_threshold,
            "loiter_seconds": self.loiter_seconds,
            "event_cooldown_seconds": self.event_cooldown_seconds,
            "high_risk_cooldown_seconds": self.high_risk_cooldown_seconds,
            "location": self.location,
            "gate_zone_enabled": self.gate_zone_enabled,
            "gate_zone_bbox_normalized": [
                self.gate_zone_x1,
                self.gate_zone_y1,
                self.gate_zone_x2,
                self.gate_zone_y2,
            ],
        }

    def get_current_events(self) -> list[dict[str, Any]]:
        return copy_security_events(self._last_current_events)

    def _track_in_gate_zone(self, track: dict[str, Any]) -> bool:
        """Return True if the track bbox centre is inside the configured gate zone.

        Coordinates are treated as normalised (0.0–1.0) frame fractions.
        If the track has no bbox or the bbox values cannot be parsed, returns
        True so the track is not silently dropped (safe fallback).
        """
        bbox = track.get("bbox")
        if not bbox or len(bbox) < 4:
            return True  # fallback: keep track if no bbox available
        try:
            x1, y1, x2, y2 = [float(v) for v in bbox[:4]]
        except (TypeError, ValueError):
            return True
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        # If bboxes look like pixel coords (any value > 1.5), skip gate-zone
        # filtering — we only filter when coords are clearly normalised.
        if max(abs(x1), abs(y1), abs(x2), abs(y2)) > 1.5:
            return True
        return (
            self.gate_zone_x1 <= cx <= self.gate_zone_x2
            and self.gate_zone_y1 <= cy <= self.gate_zone_y2
        )

    def _metrics(
        self,
        tracking_summary: dict[str, Any],
        detection_summary: dict[str, Any],
        camera_status: dict[str, Any],
        now: datetime,
    ) -> dict[str, Any]:
        tracks = tracking_summary.get("active_tracks") or []
        active_track_count = self._int(tracking_summary.get("active_track_count"), len(tracks))
        person_count = self._int(detection_summary.get("person_count"))
        phone_count = self._int(detection_summary.get("phone_count"))
        vehicle_count = self._int(detection_summary.get("vehicle_count"))
        max_track_age = 0.0
        loitering_track_ids: list[int] = []

        # Gate-zone filtering: when enabled, only count tracks in the ROI.
        if self.gate_zone_enabled:
            gate_tracks = [t for t in tracks if self._track_in_gate_zone(t)]
        else:
            gate_tracks = tracks
        active_gate_track_count = len(gate_tracks)

        for track in gate_tracks:
            age = self._float(track.get("age_seconds"))
            max_track_age = max(max_track_age, age)
            if age >= self.loiter_seconds:
                try:
                    loitering_track_ids.append(int(track["track_id"]))
                except (KeyError, TypeError, ValueError):
                    continue

        camera_is_opened = bool(camera_status.get("is_opened"))
        camera_frame_count = self._int(camera_status.get("frame_count"))
        camera_issue = not camera_is_opened or camera_frame_count <= 0
        after_hours = self._is_after_hours(now)

        return {
            "active_track_count": active_track_count,
            "active_tracks_in_gate_zone": active_gate_track_count,
            "gate_zone_enabled": self.gate_zone_enabled,
            "gate_zone_bbox_normalized": [
                self.gate_zone_x1,
                self.gate_zone_y1,
                self.gate_zone_x2,
                self.gate_zone_y2,
            ],
            "active_person_count": max(active_gate_track_count, person_count),
            "track_ids": self._track_ids(gate_tracks),
            "loitering_track_ids": loitering_track_ids,
            "max_track_age_seconds": round(max_track_age, 2),
            "person_count": person_count,
            "phone_count": phone_count,
            "vehicle_count": vehicle_count,
            "camera_is_opened": camera_is_opened,
            "camera_frame_count": camera_frame_count,
            "camera_last_error": camera_status.get("last_error"),
            "camera_issue": camera_issue,
            "after_hours": after_hours,
            "normal_start_hour": self.normal_start_hour,
            "normal_end_hour": self.normal_end_hour,
            "crowding_threshold": self.crowding_person_threshold,
            "loiter_seconds": self.loiter_seconds,
        }

    def _event(
        self,
        event_type: str,
        level: str,
        title: str,
        instruction: str,
        confidence: float,
        related_track_ids: list[int],
        evidence: dict[str, Any],
        now: datetime,
    ) -> dict[str, Any]:
        return SecurityEvent(
            event_type=event_type,
            level=level,
            title=title,
            instruction=instruction,
            confidence=round(max(0.0, min(1.0, confidence)), 3),
            location=self.location,
            related_track_ids=related_track_ids,
            evidence=evidence,
            timestamp=now.isoformat(),
        ).to_dict()

    def _build_events(
        self,
        tracking_summary: dict[str, Any],
        detection_summary: dict[str, Any],
        camera_status: dict[str, Any],
        now: datetime,
    ) -> list[dict[str, Any]]:
        evidence = self._metrics(tracking_summary, detection_summary, camera_status, now)
        events: list[dict[str, Any]] = []
        active_track_count = evidence["active_tracks_in_gate_zone"] if evidence["gate_zone_enabled"] else evidence["active_track_count"]
        active_person_count = evidence["active_person_count"]
        after_hours = evidence["after_hours"]
        crowding = active_track_count >= self.crowding_person_threshold
        loitering = bool(evidence["loitering_track_ids"])
        camera_issue = evidence["camera_issue"]

        if camera_issue:
            events.append(
                self._event(
                    "CAMERA_UNAVAILABLE",
                    "red",
                    "Camera unavailable",
                    "Check camera connection immediately.",
                    0.95,
                    [],
                    evidence,
                    now,
                )
            )

        if crowding:
            crowd_level = "orange" if active_track_count >= self.crowding_person_threshold * 2 else "yellow"
            events.append(
                self._event(
                    "CROWDING",
                    crowd_level,
                    "Crowding near entry",
                    "Check crowd movement near gate.",
                    min(0.9, 0.58 + active_track_count * 0.06),
                    evidence["track_ids"],
                    evidence,
                    now,
                )
            )

        if loitering:
            events.append(
                self._event(
                    "LOITERING",
                    "yellow",
                    "Loitering track detected",
                    "Verify the person who has stayed near the gate.",
                    min(0.9, 0.55 + evidence["max_track_age_seconds"] / 120.0),
                    evidence["loitering_track_ids"],
                    evidence,
                    now,
                )
            )

        if evidence["phone_count"] > 0:
            events.append(
                self._event(
                    "PHONE_VISIBLE_AT_GATE",
                    "yellow",
                    "Phone visible at gate",
                    "Verify phone use near the entry point.",
                    min(0.88, 0.62 + evidence["phone_count"] * 0.08),
                    evidence["track_ids"],
                    evidence,
                    now,
                )
            )

        if evidence["vehicle_count"] > 0:
            events.append(
                self._event(
                    "VEHICLE_NEAR_ENTRY",
                    "yellow",
                    "Vehicle near entry",
                    "Check vehicle position near the gate.",
                    min(0.86, 0.6 + evidence["vehicle_count"] * 0.07),
                    evidence["track_ids"],
                    evidence,
                    now,
                )
            )

        if after_hours and active_person_count > 0:
            events.append(
                self._event(
                    "AFTER_HOURS_ACTIVITY",
                    "orange",
                    "After-hours activity",
                    "Verify activity outside normal campus hours.",
                    0.82,
                    evidence["track_ids"],
                    evidence,
                    now,
                )
            )

        if camera_issue or (after_hours and (crowding or loitering)):
            events.append(
                self._event(
                    "HIGH_RISK_COMBINED",
                    "red",
                    "High-risk security condition",
                    "Escalate to the security supervisor.",
                    0.94 if camera_issue else 0.9,
                    evidence["track_ids"] or evidence["loitering_track_ids"],
                    evidence,
                    now,
                )
            )

        if not events and active_person_count > 0:
            events.append(
                self._event(
                    "NORMAL_ACTIVITY",
                    "green",
                    "Normal activity",
                    "Monitor normally.",
                    0.7,
                    evidence["track_ids"],
                    evidence,
                    now,
                )
            )

        return events

    def evaluate(
        self,
        tracking_summary: dict[str, Any],
        detection_summary: dict[str, Any],
        camera_status: dict[str, Any],
        now: datetime | None = None,
    ) -> list[dict[str, Any]]:
        if not self.rules_enabled:
            self._last_current_events = []
            return []

        current_time = self._now(now)
        current_events = self._build_events(
            tracking_summary=tracking_summary or {},
            detection_summary=detection_summary or {},
            camera_status=camera_status or {},
            now=current_time,
        )
        self._last_current_events = copy_security_events(current_events)

        emitted_events: list[dict[str, Any]] = []
        for event in current_events:
            event_type = str(event["event_type"])
            if not self._passes_cooldown(event_type, current_time):
                continue
            emitted_events.append(event)
            self._last_emitted_at[event_type] = current_time

        return copy_security_events(emitted_events)
