from dataclasses import replace

from fastapi.testclient import TestClient

import api.main as main


def test_tracking_latest_shape_without_camera_or_model():
    main.settings = replace(
        main.settings,
        yolo_enabled=False,
        tracking_enabled=True,
        camera_source="tests/no-camera.mp4",
    )

    with TestClient(main.app) as client:
        response = client.get("/api/tracking/latest")

    assert response.status_code == 200
    data = response.json()
    assert {
        "enabled",
        "tracker_type",
        "active_track_count",
        "total_tracks_seen",
        "active_tracks",
        "error",
    }.issubset(data)
    assert isinstance(data["active_tracks"], list)


def test_tracking_reset_shape_without_camera_or_model():
    main.settings = replace(
        main.settings,
        yolo_enabled=False,
        tracking_enabled=True,
        camera_source="tests/no-camera.mp4",
    )

    with TestClient(main.app) as client:
        response = client.post("/api/tracking/reset")

    assert response.status_code == 200
    data = response.json()
    assert data["reset"] is True
    assert "timestamp" in data
