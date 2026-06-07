from dataclasses import replace

from fastapi.testclient import TestClient

import api.main as main


def test_runtime_status_includes_security_status_without_camera_or_model():
    main.settings = replace(
        main.settings,
        yolo_enabled=False,
        tracking_enabled=True,
        camera_source="tests/no-camera.mp4",
        security_rules_enabled=True,
    )

    with TestClient(main.app) as client:
        response = client.get("/api/runtime/status")

    assert response.status_code == 200
    data = response.json()
    assert "security_status" in data
    assert data["security_status"]["rules_enabled"] is True
    assert "latest_level" in data["security_status"]
