"""
tests/test_milestone_2d_api.py — Milestone 2D

Unit tests for the Multi-Modal Risk Fusion API endpoint.
"""

from __future__ import annotations

from fastapi.testclient import TestClient
import api.main
from api.main import app
from core.face_verification import FaceVerificationResult, FaceVerificationStatus


def test_api_risk_fusion_status_default():
    with TestClient(app) as client:
        # Clear any stored face verification result
        api.main.latest_face_verification_result = None

        response = client.get("/api/risk-fusion/status")
        assert response.status_code == 200
        data = response.json()
        
        # Verify JSON schema output keys
        assert "level" in data
        assert "score" in data
        assert "reasons" in data
        assert "recommended_action" in data
        assert "human_review_required" in data
        assert "privacy_note" in data
        
        # Default with no face and camera offline or online should be evaluated properly
        assert data["level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
        assert isinstance(data["score"], int)
        assert data["human_review_required"] is True
        assert "privacy" in data["privacy_note"].lower()


def test_api_risk_fusion_status_overrides():
    with TestClient(app) as client:
        # Case 1: Unknown face + after hours -> CRITICAL
        response = client.get(
            "/api/risk-fusion/status",
            params={
                "face_status": "UNKNOWN",
                "after_hours": "true",
                "camera_available": "true",
                "security_level": "green",
                "security_event_type": "NORMAL_ACTIVITY"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["level"] == "CRITICAL"
        assert data["score"] >= 85
        assert any("after-hours" in reason.lower() for reason in data["reasons"])

        # Case 2: Camera unavailable -> HIGH or CRITICAL
        response = client.get(
            "/api/risk-fusion/status",
            params={"camera_available": "false"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["level"] in ("HIGH", "CRITICAL")
        assert data["score"] >= 75

        # Case 3: Known face + normal parameters -> LOW
        response = client.get(
            "/api/risk-fusion/status",
            params={
                "face_status": "KNOWN",
                "after_hours": "false",
                "camera_available": "true",
                "motionless_person": "false",
                "active_tracks_in_gate_zone": 0,
                "security_level": "green",
                "security_event_type": "NORMAL_ACTIVITY"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["level"] == "LOW"
        assert data["score"] <= 30


def test_api_risk_fusion_mitigations():
    with TestClient(app) as client:
        # Case 1: Unknown face with no cues (starts at 70 -> HIGH)
        response_no_cues = client.get(
            "/api/risk-fusion/status",
            params={
                "face_status": "UNKNOWN",
                "camera_available": "true",
                "after_hours": "false",
                "active_tracks_in_gate_zone": 0,
                "security_level": "green",
                "security_event_type": "NORMAL_ACTIVITY"
            }
        )
        data_no_cues = response_no_cues.json()
        assert data_no_cues["level"] == "HIGH"
        assert data_no_cues["score"] == 70

        # Case 2: Unknown face with lanyard and id_card (score drops but floored at 50)
        response_with_cues = client.get(
            "/api/risk-fusion/status",
            params={
                "face_status": "UNKNOWN",
                "camera_available": "true",
                "after_hours": "false",
                "active_tracks_in_gate_zone": 0,
                "object_cues_detected": "lanyard,id_card",
                "security_level": "green",
                "security_event_type": "NORMAL_ACTIVITY"
            }
        )
        data_with_cues = response_with_cues.json()
        # 70 - 10 = 60 -> MEDIUM
        assert data_with_cues["level"] == "MEDIUM"
        assert data_with_cues["score"] == 60


def test_api_face_verify_updates_fusion():
    with TestClient(app) as client:
        # Simulate a face verification run returning a KNOWN face match
        mock_result = FaceVerificationResult(
            status=FaceVerificationStatus.VERIFIED_KNOWN_MEMBER,
            display_color="green",
            confidence=0.88,
            matched_member="Demo Member A",
            instruction="Verified known face match",
            face_count=1,
            processing_ms=12.5
        )
        api.main.latest_face_verification_result = mock_result

        # Fetch risk fusion status and make sure it picks up the face status as KNOWN
        response = client.get(
            "/api/risk-fusion/status",
            params={
                "camera_available": "true",
                "after_hours": "false",
                "motionless_person": "false",
                "active_tracks_in_gate_zone": 0,
                "security_level": "green",
                "security_event_type": "NORMAL_ACTIVITY"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["level"] == "LOW"
        assert data["score"] <= 30
        assert any("known face" in reason.lower() for reason in data["reasons"])

