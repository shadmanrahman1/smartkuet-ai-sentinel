from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def isoformat(value: datetime) -> str:
    return value.isoformat()


def bbox_iou(box_a: list[float], box_b: list[float]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_width = max(0.0, inter_x2 - inter_x1)
    inter_height = max(0.0, inter_y2 - inter_y1)
    intersection = inter_width * inter_height

    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - intersection
    if union <= 0:
        return 0.0
    return intersection / union


@dataclass
class TrackState:
    track_id: int
    bbox: list[float]
    class_name: str
    confidence: float
    first_seen_dt: datetime = field(default_factory=utc_now)
    last_seen_dt: datetime = field(default_factory=utc_now)
    missed_frames: int = 0

    @property
    def first_seen(self) -> str:
        return isoformat(self.first_seen_dt)

    @property
    def last_seen(self) -> str:
        return isoformat(self.last_seen_dt)

    @property
    def age_seconds(self) -> float:
        return max(0.0, (self.last_seen_dt - self.first_seen_dt).total_seconds())

    def to_dict(self) -> dict[str, Any]:
        return {
            "track_id": self.track_id,
            "class_name": self.class_name,
            "confidence": self.confidence,
            "bbox": self.bbox,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "age_seconds": round(self.age_seconds, 2),
            "missed_frames": self.missed_frames,
        }


class PersonTracker:
    def __init__(
        self,
        tracker_type: str = "bytetrack",
        max_age_seconds: float = 5.0,
        iou_threshold: float = 0.5,
        person_class_name: str = "person",
        min_confidence: float = 0.35,
        max_missed_frames: int = 10,
    ):
        self.requested_tracker_type = tracker_type
        self.backend = "iou_fallback"
        self.max_age_seconds = max_age_seconds
        self.iou_threshold = iou_threshold
        self.person_class_name = person_class_name
        self.min_confidence = min_confidence
        self.max_missed_frames = max(1, int(max_missed_frames))
        self._tracks: dict[int, TrackState] = {}
        self._next_track_id = 1
        self.total_tracks_seen = 0
        self.last_error: str | None = None

    @property
    def active_tracks(self) -> list[dict[str, Any]]:
        return [track.to_dict() for track in self._tracks.values()]

    def reset(self) -> None:
        self._tracks.clear()
        self._next_track_id = 1
        self.total_tracks_seen = 0
        self.last_error = None

    def _new_track(self, detection: dict[str, Any], now: datetime) -> TrackState:
        track = TrackState(
            track_id=self._next_track_id,
            bbox=[float(value) for value in detection["bbox"]],
            class_name=self.person_class_name,
            confidence=float(detection.get("confidence", 0.0)),
            first_seen_dt=now,
            last_seen_dt=now,
        )
        self._tracks[track.track_id] = track
        self._next_track_id += 1
        self.total_tracks_seen += 1
        return track

    def _prune_old_tracks(self, now: datetime) -> None:
        expired_ids = [
            track_id
            for track_id, track in self._tracks.items()
            if (
                (now - track.last_seen_dt).total_seconds() > self.max_age_seconds
                or track.missed_frames > self.max_missed_frames
            )
        ]
        for track_id in expired_ids:
            self._tracks.pop(track_id, None)

    def update(
        self,
        frame: Any,
        detections: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        del frame
        now = utc_now()
        person_detections = [
            detection
            for detection in detections
            if detection.get("class_name") == self.person_class_name
            and float(detection.get("confidence", 0.0)) >= self.min_confidence
        ]

        matched_track_ids: set[int] = set()
        updated_tracks: list[TrackState] = []

        for detection in person_detections:
            bbox = [float(value) for value in detection["bbox"]]
            best_track: TrackState | None = None
            best_iou = 0.0

            for track in self._tracks.values():
                if track.track_id in matched_track_ids:
                    continue
                iou = bbox_iou(track.bbox, bbox)
                if iou > best_iou:
                    best_iou = iou
                    best_track = track

            if best_track is not None and best_iou >= self.iou_threshold:
                best_track.bbox = bbox
                best_track.confidence = float(detection.get("confidence", 0.0))
                best_track.last_seen_dt = now
                best_track.missed_frames = 0
                matched_track_ids.add(best_track.track_id)
                updated_tracks.append(best_track)
            else:
                new_track = self._new_track(detection, now)
                matched_track_ids.add(new_track.track_id)
                updated_tracks.append(new_track)

        for track in self._tracks.values():
            if track.track_id not in matched_track_ids:
                track.missed_frames += 1

        self._prune_old_tracks(now)
        return [track.to_dict() for track in updated_tracks]

    def get_status(self) -> dict[str, Any]:
        return {
            "enabled": True,
            "tracker_type": self.backend,
            "requested_tracker_type": self.requested_tracker_type,
            "active_track_count": len(self._tracks),
            "total_tracks_seen": self.total_tracks_seen,
            "active_tracks": self.active_tracks,
            "max_age_seconds": self.max_age_seconds,
            "max_missed_frames": self.max_missed_frames,
            "iou_threshold": self.iou_threshold,
            "last_error": self.last_error,
        }
