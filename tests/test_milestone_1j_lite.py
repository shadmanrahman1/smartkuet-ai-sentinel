"""
Milestone 1J-lite tests.

No YOLO model loading. No webcam/video source required.
Tests cover:
 - Gate-zone ROI filtering in security rules
 - Security rules fallback without frame dimensions (pixel-coord bboxes)
 - Tracker missed_frames pruning threshold
 - CUDA setup doc exists and contains required text
 - Runtime config has gate-zone and missed-frames fields
"""

from datetime import datetime, timezone

import pytest

from core.security_rules import SecurityRulesEngine
from core.tracker import PersonTracker


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

NOON = datetime(2026, 6, 7, 12, 0, tzinfo=timezone.utc)


def camera_ok() -> dict:
    return {"is_opened": True, "frame_count": 5, "last_error": None}


def detection_summary(person_count: int = 0) -> dict:
    return {
        "enabled": True,
        "total": person_count,
        "person_count": person_count,
        "phone_count": 0,
        "vehicle_count": 0,
        "classes": {},
        "error": None,
    }


def make_track(track_id: int, bbox: list, age: float = 1.0) -> dict:
    return {
        "track_id": track_id,
        "class_name": "person",
        "confidence": 0.8,
        "bbox": bbox,
        "age_seconds": age,
        "missed_frames": 0,
    }


def tracking_summary_with_tracks(tracks: list[dict]) -> dict:
    return {
        "enabled": True,
        "tracker_type": "iou_fallback",
        "active_track_count": len(tracks),
        "total_tracks_seen": len(tracks),
        "active_tracks": tracks,
        "error": None,
    }


# ---------------------------------------------------------------------------
# 1. Gate-zone filtering: only tracks INSIDE the ROI are counted for crowding
# ---------------------------------------------------------------------------

def test_gate_zone_counts_only_tracks_inside_roi():
    """Engine with gate_zone_enabled=True should only count tracks whose
    normalized bbox centre falls inside the configured ROI."""
    engine = SecurityRulesEngine(
        crowding_person_threshold=2,
        gate_zone_enabled=True,
        gate_zone_x1=0.0,
        gate_zone_y1=0.0,
        gate_zone_x2=0.5,   # right half excluded
        gate_zone_y2=1.0,
    )

    # Two tracks: one inside (cx=0.25), one outside (cx=0.75)
    inside_track = make_track(1, [0.1, 0.1, 0.4, 0.9])   # cx=0.25 ✓
    outside_track = make_track(2, [0.6, 0.1, 0.9, 0.9])  # cx=0.75 ✗

    events = engine.evaluate(
        tracking_summary=tracking_summary_with_tracks([inside_track, outside_track]),
        detection_summary=detection_summary(person_count=2),
        camera_status=camera_ok(),
        now=NOON,
    )

    # Only 1 track inside zone → below threshold of 2 → no CROWDING
    event_types = {e["event_type"] for e in events}
    assert "CROWDING" not in event_types


def test_gate_zone_triggers_crowding_when_enough_tracks_inside():
    """When enough tracks are inside the gate zone, CROWDING should fire."""
    engine = SecurityRulesEngine(
        crowding_person_threshold=2,
        gate_zone_enabled=True,
        gate_zone_x1=0.0,
        gate_zone_y1=0.0,
        gate_zone_x2=1.0,
        gate_zone_y2=1.0,
    )

    t1 = make_track(1, [0.1, 0.1, 0.4, 0.9])
    t2 = make_track(2, [0.5, 0.1, 0.8, 0.9])

    events = engine.evaluate(
        tracking_summary=tracking_summary_with_tracks([t1, t2]),
        detection_summary=detection_summary(person_count=2),
        camera_status=camera_ok(),
        now=NOON,
    )

    event_types = {e["event_type"] for e in events}
    assert "CROWDING" in event_types


# ---------------------------------------------------------------------------
# 2. Fallback: pixel-coord bboxes are NOT filtered out by gate zone
# ---------------------------------------------------------------------------

def test_gate_zone_fallback_with_pixel_coords():
    """Pixel-coordinate bboxes (values > 1.5) should bypass gate-zone filtering
    and be treated as 'inside' so no tracks are silently dropped."""
    engine = SecurityRulesEngine(
        crowding_person_threshold=2,
        gate_zone_enabled=True,
        gate_zone_x1=0.0,
        gate_zone_y1=0.0,
        gate_zone_x2=0.3,  # Very narrow zone — would exclude pixel coords
        gate_zone_y2=0.3,
    )

    # Pixel-coordinate bbox (would be outside zone if mistakenly treated as normalised)
    t1 = make_track(1, [100, 200, 300, 400])
    t2 = make_track(2, [400, 200, 600, 400])

    events = engine.evaluate(
        tracking_summary=tracking_summary_with_tracks([t1, t2]),
        detection_summary=detection_summary(person_count=2),
        camera_status=camera_ok(),
        now=NOON,
    )

    # Both tracks should pass through → CROWDING should fire
    event_types = {e["event_type"] for e in events}
    assert "CROWDING" in event_types


def test_gate_zone_disabled_counts_all_tracks():
    """When gate_zone_enabled=False, all tracks count regardless of position."""
    engine = SecurityRulesEngine(
        crowding_person_threshold=2,
        gate_zone_enabled=False,
    )

    # Two tracks well outside a hypothetical zone — all should count
    t1 = make_track(1, [0.0, 0.0, 0.1, 0.1])
    t2 = make_track(2, [0.9, 0.9, 1.0, 1.0])

    events = engine.evaluate(
        tracking_summary=tracking_summary_with_tracks([t1, t2]),
        detection_summary=detection_summary(person_count=2),
        camera_status=camera_ok(),
        now=NOON,
    )

    event_types = {e["event_type"] for e in events}
    assert "CROWDING" in event_types


# ---------------------------------------------------------------------------
# 3. Tracker: missed_frames pruning
# ---------------------------------------------------------------------------

def test_tracker_prunes_after_missed_frames_threshold():
    """Tracks should be pruned after missed_frames exceeds max_missed_frames
    even if they have not yet exceeded the time-based age limit."""
    tracker = PersonTracker(max_age_seconds=9999, max_missed_frames=3)

    # Create a track by feeding a detection
    detections = [{"class_name": "person", "confidence": 0.9, "bbox": [0, 0, 50, 100]}]
    tracker.update(None, detections)
    assert tracker.get_status()["active_track_count"] == 1

    # Miss 4 frames with no detections — should exceed threshold of 3
    for _ in range(4):
        tracker.update(None, [])

    assert tracker.get_status()["active_track_count"] == 0


def test_tracker_keeps_track_within_missed_frames_threshold():
    """Tracks with missed_frames at or below the threshold should stay alive."""
    tracker = PersonTracker(max_age_seconds=9999, max_missed_frames=5)

    detections = [{"class_name": "person", "confidence": 0.9, "bbox": [0, 0, 50, 100]}]
    tracker.update(None, detections)

    # Miss 3 frames — within threshold of 5
    for _ in range(3):
        tracker.update(None, [])

    assert tracker.get_status()["active_track_count"] == 1


# ---------------------------------------------------------------------------
# 4. CUDA setup doc exists and contains required content
# ---------------------------------------------------------------------------

def test_cuda_setup_doc_exists():
    from pathlib import Path
    doc = Path(__file__).resolve().parents[1] / "docs" / "local_cuda_setup.md"
    assert doc.exists(), "docs/local_cuda_setup.md should exist"


def test_cuda_setup_doc_contains_cpu_mode_note():
    from pathlib import Path
    doc = Path(__file__).resolve().parents[1] / "docs" / "local_cuda_setup.md"
    content = doc.read_text(encoding="utf-8")
    assert "CPU mode" in content, "CUDA setup doc should mention 'CPU mode'"
    assert "rollback" in content.lower(), "CUDA setup doc should mention rollback"


# ---------------------------------------------------------------------------
# 5. Runtime config includes gate-zone and missed-frames fields
# ---------------------------------------------------------------------------

def test_settings_have_gate_zone_fields():
    from core.config import settings
    assert hasattr(settings, "gate_zone_enabled")
    assert hasattr(settings, "gate_zone_x1")
    assert hasattr(settings, "gate_zone_y1")
    assert hasattr(settings, "gate_zone_x2")
    assert hasattr(settings, "gate_zone_y2")
    # Defaults are sensible floats in [0, 1]
    for attr in ("gate_zone_x1", "gate_zone_y1", "gate_zone_x2", "gate_zone_y2"):
        val = getattr(settings, attr)
        assert 0.0 <= val <= 1.0, f"{attr}={val} should be normalised"


def test_settings_have_max_track_missed_frames():
    from core.config import settings
    assert hasattr(settings, "max_track_missed_frames")
    assert settings.max_track_missed_frames >= 1


def test_security_rules_engine_get_config_includes_gate_zone():
    engine = SecurityRulesEngine(gate_zone_enabled=True, gate_zone_x1=0.2)
    config = engine.get_config()
    assert "gate_zone_enabled" in config
    assert config["gate_zone_enabled"] is True
    assert "gate_zone_bbox_normalized" in config
    assert len(config["gate_zone_bbox_normalized"]) == 4
