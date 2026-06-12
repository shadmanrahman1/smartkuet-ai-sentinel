"""
tests/test_milestone_2d_risk_fusion.py — Milestone 2D

Verification tests for the Multi-Modal Risk Fusion Engine.
"""

from __future__ import annotations

from core.risk_fusion import RiskFusionInput, evaluate_risk, RiskLevel


def test_known_face_normal_activity_is_low():
    inputs = RiskFusionInput(
        face_status="KNOWN",
        camera_available=True,
        after_hours=False,
        security_level="green",
        security_event_type="NORMAL_ACTIVITY"
    )
    result = evaluate_risk(inputs)
    assert result.level == RiskLevel.LOW
    assert result.score <= 30
    assert result.human_review_required is True
    assert "Verified known face" in "".join(result.reasons)
    assert "privacy" in result.privacy_note.lower()


def test_unknown_face_in_gate_zone_is_high():
    inputs = RiskFusionInput(
        face_status="UNKNOWN",
        active_tracks_in_gate_zone=1,
        camera_available=True,
        after_hours=False
    )
    result = evaluate_risk(inputs)
    assert result.level == RiskLevel.HIGH
    assert result.score >= 70
    assert result.score < 85
    assert "gate-zone" in "".join(result.reasons).lower() or "unrecognized face" in "".join(result.reasons).lower()


def test_unknown_face_after_hours_is_critical():
    inputs = RiskFusionInput(
        face_status="UNKNOWN",
        after_hours=True,
        camera_available=True
    )
    result = evaluate_risk(inputs)
    assert result.level == RiskLevel.CRITICAL
    assert result.score >= 85
    assert "after-hours" in "".join(result.reasons).lower()


def test_low_confidence_face_is_medium():
    inputs = RiskFusionInput(
        face_status="LOW_CONFIDENCE",
        camera_available=True,
        after_hours=False
    )
    result = evaluate_risk(inputs)
    assert result.level == RiskLevel.MEDIUM
    assert result.score >= 30
    assert result.score < 70
    assert "low confidence" in "".join(result.reasons).lower()


def test_object_cue_mitigates_but_never_proves_identity_alone():
    # Test 1: Unknown face with no cues (starts at 70 -> HIGH)
    inputs_no_cues = RiskFusionInput(
        face_status="UNKNOWN",
        camera_available=True,
        object_cues_detected=[]
    )
    res_no_cues = evaluate_risk(inputs_no_cues)
    assert res_no_cues.level == RiskLevel.HIGH
    
    # Test 2: Unknown face with cues (score drops slightly but cannot be LOW)
    inputs_with_cues = RiskFusionInput(
        face_status="UNKNOWN",
        camera_available=True,
        object_cues_detected=["lanyard", "id_card"]
    )
    res_with_cues = evaluate_risk(inputs_with_cues)
    # 70 - 10 = 60 (MEDIUM)
    assert res_with_cues.score == 60
    assert res_with_cues.level == RiskLevel.MEDIUM  # mitigates down to MEDIUM
    
    # Test 3: Even with all possible cues, unknown face score is floored at 50, preventing LOW status
    inputs_all_cues = RiskFusionInput(
        face_status="UNKNOWN",
        camera_available=True,
        object_cues_detected=["lanyard", "id_card", "visitor_badge"]
    )
    res_all_cues = evaluate_risk(inputs_all_cues)
    assert res_all_cues.score == 55  # 70 - 15 = 55 (which is above the floor of 50)
    assert res_all_cues.level == RiskLevel.MEDIUM

    # Test 4: Low-confidence face (base score 45) with all cues (mitigation 15) is floored at 30
    inputs_low_conf_all_cues = RiskFusionInput(
        face_status="LOW_CONFIDENCE",
        camera_available=True,
        object_cues_detected=["lanyard", "id_card", "visitor_badge"]
    )
    res_low_conf_all_cues = evaluate_risk(inputs_low_conf_all_cues)
    assert res_low_conf_all_cues.score == 30  # 45 - 15 = 30 (exact floor)
    assert res_low_conf_all_cues.level == RiskLevel.MEDIUM


def test_camera_unavailable_is_high():
    inputs = RiskFusionInput(
        camera_available=False,
        face_status="KNOWN"
    )
    result = evaluate_risk(inputs)
    assert result.level == RiskLevel.HIGH
    assert result.score >= 70
    assert "camera" in "".join(result.reasons).lower() or "offline" in "".join(result.reasons).lower()


def test_motionless_person_after_hours_is_critical():
    inputs = RiskFusionInput(
        motionless_person=True,
        after_hours=True,
        face_status="KNOWN"
    )
    result = evaluate_risk(inputs)
    assert result.level == RiskLevel.CRITICAL
    assert result.score >= 85
    assert "motionless" in "".join(result.reasons).lower()


def test_human_review_and_privacy_present():
    inputs = RiskFusionInput()
    result = evaluate_risk(inputs)
    assert result.human_review_required is True
    assert len(result.privacy_note) > 10
