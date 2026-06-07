from dataclasses import replace

from fastapi.testclient import TestClient

import api.main as main


def test_health_returns_ok():
    main.settings = replace(
        main.settings,
        yolo_enabled=False,
        camera_source="tests/no-camera.mp4",
    )

    with TestClient(main.app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "app": "SmartKUET Sentinel"}
