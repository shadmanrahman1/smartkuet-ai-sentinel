from dataclasses import replace

from fastapi.testclient import TestClient

import api.main as main


def test_security_status_shape_without_camera_or_model():
    main.settings = replace(
        main.settings,
        yolo_enabled=False,
        tracking_enabled=True,
        camera_source="tests/no-camera.mp4",
        security_rules_enabled=True,
    )

    with TestClient(main.app) as client:
        response = client.get("/api/security/status")

    assert response.status_code == 200
    data = response.json()
    expected = {
        "rules_enabled",
        "latest_events",
        "latest_level",
        "latest_event_type",
        "latest_instruction",
        "last_event_at",
        "cooldowns",
        "crowding_person_threshold",
        "loiter_seconds",
        "location",
    }
    assert expected.issubset(data)
    assert data["rules_enabled"] is True
    assert isinstance(data["latest_events"], list)


def test_security_rules_reset_shape_without_camera_or_model():
    main.settings = replace(
        main.settings,
        yolo_enabled=False,
        tracking_enabled=True,
        camera_source="tests/no-camera.mp4",
        security_rules_enabled=True,
    )

    with TestClient(main.app) as client:
        response = client.post("/api/security/rules/reset")

    assert response.status_code == 200
    data = response.json()
    assert data["reset"] is True
    assert "timestamp" in data
    assert "security_status" in data
