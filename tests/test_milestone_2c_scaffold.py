"""
tests/test_milestone_2c_scaffold.py — Milestone 2C

Tests for local-only object-cue detection service scaffold.
"""

from __future__ import annotations

from pathlib import Path
from fastapi.testclient import TestClient

from core.config import Settings
from core.object_cue_detection import ObjectCueDetectionService, ObjectCueStatus
from api.main import app


def test_object_cue_service_disabled():
    service = ObjectCueDetectionService(enabled=False, model_path=Path("models/object_cues/best.pt"))
    status = service.get_status()
    assert status["enabled"] is False
    assert status["configured"] is False
    assert status["status"] == ObjectCueStatus.DISABLED
    assert "disabled" in status["instruction"].lower()
    assert "id_card" in status["supported_cues"]


def test_object_cue_service_model_not_configured_when_missing():
    # Set path to a non-existent model file
    service = ObjectCueDetectionService(
        enabled=True,
        model_path=Path("models/object_cues/does_not_exist.pt"),
        supported_cues=["id_card", "lanyard"]
    )
    status = service.get_status()
    assert status["enabled"] is True
    assert status["configured"] is False
    assert status["status"] == ObjectCueStatus.MODEL_NOT_CONFIGURED
    assert "missing" in status["instruction"].lower() or "not configured" in status["instruction"].lower()
    assert status["supported_cues"] == ["id_card", "lanyard"]


def test_object_cue_service_ready_when_model_exists(tmp_path):
    # Simulate existing model weights
    dummy_model = tmp_path / "best.pt"
    dummy_model.write_text("dummy model weights")
    
    service = ObjectCueDetectionService(enabled=True, model_path=dummy_model)
    status = service.get_status()
    assert status["enabled"] is True
    assert status["configured"] is True
    assert status["status"] == ObjectCueStatus.READY
    assert "ready" in status["instruction"].lower()


def test_api_object_cues_status_endpoint():
    with TestClient(app) as client:
        response = client.get("/api/object-cues/status")
        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data
        assert "configured" in data
        assert "model_path" in data
        assert "status" in data
        assert "supported_cues" in data
        assert "instruction" in data


def test_gitignore_protects_object_cue_assets():
    gitignore_path = Path(__file__).resolve().parents[1] / ".gitignore"
    assert gitignore_path.exists()
    content = gitignore_path.read_text()
    
    # Check that model weights, datasets, and runs are ignored
    assert "models/object_cues/*" in content
    assert "data/roboflow_datasets/*" in content
    assert "runs/object_cues/*" in content
    
    # And make sure placeholders are excluded from gitignore
    assert "!models/object_cues/.gitkeep" in content
    assert "!data/roboflow_datasets/.gitkeep" in content
    assert "!runs/object_cues/.gitkeep" in content
