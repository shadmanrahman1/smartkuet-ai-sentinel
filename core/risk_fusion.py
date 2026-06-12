"""
core/risk_fusion.py — Milestone 2D

Deterministic Multi-Modal Risk Fusion Engine.
Pure Python only (no external API dependencies, no OpenCV, no YOLO/InsightFace files).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


class RiskLevel:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class RiskFusionInput:
    """Inputs to the Multi-Modal Risk Fusion Engine."""
    security_level: str = "green"  # green, yellow, orange, red
    security_event_type: str = "NORMAL_ACTIVITY"
    active_tracks: int = 0
    active_tracks_in_gate_zone: int = 0
    face_status: str = "NOT_AVAILABLE"  # KNOWN, LOW_CONFIDENCE, UNKNOWN, NOT_AVAILABLE
    object_cue_status: str = "DISABLED"  # READY, DISABLED, MODEL_NOT_CONFIGURED
    object_cues_detected: list[str] = field(default_factory=list)
    after_hours: bool = False
    camera_available: bool = True
    motionless_person: bool = False
    human_review_required: bool = True


@dataclass
class RiskFusionResult:
    """Unified output of the Risk Fusion Engine."""
    level: str  # LOW, MEDIUM, HIGH, CRITICAL
    score: int  # 0 to 100
    reasons: list[str]
    recommended_action: str
    human_review_required: bool
    privacy_note: str


def evaluate_risk(inputs: RiskFusionInput) -> RiskFusionResult:
    """
    Evaluate and fuse multi-modal inputs into a single risk verdict.
    All calculations are deterministic, explainable, and local.
    """
    reasons: list[str] = []
    score = 0

    # 1. Base Score from Face Status
    if inputs.face_status == "KNOWN":
        score = 15
        reasons.append("Verified known face match.")
    elif inputs.face_status == "LOW_CONFIDENCE":
        score = 45
        reasons.append("Low confidence face verification match.")
    elif inputs.face_status == "UNKNOWN":
        score = 70
        reasons.append("Unrecognized face detected.")
    else:  # NOT_AVAILABLE or others
        score = 30
        reasons.append("Face verification not available or no face in view.")

    # 2. Aggravating Factors
    # After Hours
    if inputs.after_hours:
        if inputs.face_status == "UNKNOWN":
            score = 90
            reasons.append("After-hours activity with unrecognized face.")
        else:
            score += 20
            reasons.append("Activity observed during after-hours.")

    # Motionless Person
    if inputs.motionless_person:
        if inputs.after_hours:
            score = max(score, 90)
            reasons.append("Motionless person detected during after-hours.")
        else:
            score = max(score, 75)
            reasons.append("Motionless person detected in gate area.")

    # Camera Offline
    if not inputs.camera_available:
        score = max(score, 75)
        reasons.append("Camera feed is offline or unavailable.")

    # Gate-Zone Presence
    if inputs.active_tracks_in_gate_zone > 0 and inputs.face_status == "UNKNOWN":
        score = max(score, 75)
        reasons.append("Unrecognized face present inside gate-zone ROI.")

    # Red/High-risk Security Rule Triggered
    if inputs.security_level == "red" or inputs.security_event_type == "HIGH_RISK_COMBINED":
        if inputs.after_hours:
            score = max(score, 95)
            reasons.append("Critical security alert combined with after-hours.")
        else:
            score = max(score, 80)
            reasons.append("High-risk security rule triggered.")

    # 3. Mitigating Factors (Object Cues like lanyard, ID card, or visitor badge)
    # Mitigating factors can slightly lower the uncertainty/risk score,
    # but cannot verify identity or drop the level to LOW on their own.
    if inputs.face_status in ("UNKNOWN", "LOW_CONFIDENCE"):
        mitigations = 0
        for cue in ["lanyard", "id_card", "visitor_badge"]:
            if cue in inputs.object_cues_detected:
                mitigations += 5
                reasons.append(f"Mitigating cue detected: {cue.replace('_', ' ')}.")
        
        # Apply score reductions
        score = max(score - mitigations, 0)
        
        # Enforce safety score floors so cues alone cannot masquerade as verification
        if inputs.face_status == "UNKNOWN":
            score = max(score, 50)
        elif inputs.face_status == "LOW_CONFIDENCE":
            score = max(score, 30)

    # 4. Map Final Score to Risk Level
    score = min(max(score, 0), 100)
    if score >= 85:
        level = RiskLevel.CRITICAL
        recommended_action = "Sound alert; escalate to supervisor immediately."
    elif score >= 70:
        level = RiskLevel.HIGH
        recommended_action = "Inspect credentials and escalate query."
    elif score >= 30:
        level = RiskLevel.MEDIUM
        recommended_action = "Request manual ID verification."
    else:
        level = RiskLevel.LOW
        recommended_action = "Allow entry; monitor normally."

    privacy_note = (
        "Privacy Notice: The risk fusion engine runs locally. Open-source demo identities "
        "only. No real student biometric profiles are queried or stored."
    )

    return RiskFusionResult(
        level=level,
        score=score,
        reasons=reasons,
        recommended_action=recommended_action,
        human_review_required=inputs.human_review_required,
        privacy_note=privacy_note,
    )
