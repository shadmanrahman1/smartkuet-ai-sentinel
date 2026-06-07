from datetime import datetime, timezone

from core.security_rules import SecurityRulesEngine


NOON = datetime(2026, 6, 7, 12, 0, tzinfo=timezone.utc)
AFTER_HOURS = datetime(2026, 6, 7, 23, 0, tzinfo=timezone.utc)


def camera_ok() -> dict:
    return {
        "is_opened": True,
        "frame_count": 5,
        "last_error": None,
    }


def detection_summary(person_count: int = 0, phone_count: int = 0, vehicle_count: int = 0) -> dict:
    return {
        "enabled": True,
        "total": person_count + phone_count + vehicle_count,
        "person_count": person_count,
        "phone_count": phone_count,
        "vehicle_count": vehicle_count,
        "classes": {},
        "error": None,
    }


def tracking_summary(*ages: float) -> dict:
    tracks = [
        {
            "track_id": index + 1,
            "class_name": "person",
            "confidence": 0.8,
            "bbox": [0, 0, 20, 40],
            "age_seconds": age,
        }
        for index, age in enumerate(ages)
    ]
    return {
        "enabled": True,
        "tracker_type": "iou_fallback",
        "active_track_count": len(tracks),
        "total_tracks_seen": len(tracks),
        "active_tracks": tracks,
        "error": None,
    }


def event_types(events: list[dict]) -> set[str]:
    return {event["event_type"] for event in events}


def test_no_people_camera_ok_has_no_high_risk_event():
    engine = SecurityRulesEngine()

    events = engine.evaluate(
        tracking_summary=tracking_summary(),
        detection_summary=detection_summary(),
        camera_status=camera_ok(),
        now=NOON,
    )

    assert "HIGH_RISK_COMBINED" not in event_types(events)
    assert events == []


def test_crowding_event_when_active_tracks_reach_threshold():
    engine = SecurityRulesEngine(crowding_person_threshold=4)

    events = engine.evaluate(
        tracking_summary=tracking_summary(1, 1, 1, 1),
        detection_summary=detection_summary(person_count=4),
        camera_status=camera_ok(),
        now=NOON,
    )

    assert "CROWDING" in event_types(events)
    crowding = next(event for event in events if event["event_type"] == "CROWDING")
    assert crowding["level"] == "yellow"
    assert crowding["evidence"]["active_track_count"] == 4


def test_loitering_event_when_track_age_exceeds_threshold():
    engine = SecurityRulesEngine(loiter_seconds=15)

    events = engine.evaluate(
        tracking_summary=tracking_summary(20),
        detection_summary=detection_summary(person_count=1),
        camera_status=camera_ok(),
        now=NOON,
    )

    assert "LOITERING" in event_types(events)
    loitering = next(event for event in events if event["event_type"] == "LOITERING")
    assert loitering["related_track_ids"] == [1]


def test_phone_visible_event_from_detection_summary():
    engine = SecurityRulesEngine()

    events = engine.evaluate(
        tracking_summary=tracking_summary(),
        detection_summary=detection_summary(phone_count=1),
        camera_status=camera_ok(),
        now=NOON,
    )

    assert "PHONE_VISIBLE_AT_GATE" in event_types(events)


def test_camera_closed_is_red_security_event():
    engine = SecurityRulesEngine()

    events = engine.evaluate(
        tracking_summary=tracking_summary(),
        detection_summary=detection_summary(),
        camera_status={"is_opened": False, "frame_count": 0, "last_error": "closed"},
        now=NOON,
    )

    assert "CAMERA_UNAVAILABLE" in event_types(events)
    assert any(event["level"] == "red" for event in events)


def test_after_hours_active_person_is_orange():
    engine = SecurityRulesEngine(normal_start_hour=6, normal_end_hour=22)

    events = engine.evaluate(
        tracking_summary=tracking_summary(1),
        detection_summary=detection_summary(person_count=1),
        camera_status=camera_ok(),
        now=AFTER_HOURS,
    )

    assert "AFTER_HOURS_ACTIVITY" in event_types(events)
    after_hours = next(
        event for event in events if event["event_type"] == "AFTER_HOURS_ACTIVITY"
    )
    assert after_hours["level"] == "orange"


def test_cooldown_prevents_duplicate_event():
    engine = SecurityRulesEngine(
        crowding_person_threshold=2,
        event_cooldown_seconds=10,
    )

    first = engine.evaluate(
        tracking_summary=tracking_summary(1, 1),
        detection_summary=detection_summary(person_count=2),
        camera_status=camera_ok(),
        now=NOON,
    )
    second = engine.evaluate(
        tracking_summary=tracking_summary(1, 1),
        detection_summary=detection_summary(person_count=2),
        camera_status=camera_ok(),
        now=NOON,
    )

    assert "CROWDING" in event_types(first)
    assert second == []
