# Multi-Modal Risk Fusion Engine Design

This document details the architectural design and rules framework for the **Multi-Modal Risk Fusion Engine** implemented in Milestone 2D of SmartKUET Sentinel.

---

## 1. Research Contribution & Academic Framing

In a typical campus gate security environment, individual sensors or detection models are prone to high false-alarm rates or incomplete context. For example:
1. **Face Verification** can fail due to occlusion (helmets, scarves), motion blur, or bad lighting.
2. **Object Detection** (lanyards, ID badges) can detect a badge but cannot prove the bearer is the authorized cardholder.
3. **Temporal/Spatial Rules** (after-hours activity, loitering) indicate suspicious behavior but do not confirm identity.

The **Multi-Modal Risk Fusion Engine** represents the primary **academic and research contribution** of the SmartKUET Sentinel project. It aggregates diverse signal streams into a single, explainable, and deterministic security risk level:

```
┌──────────────────┐     ┌─────────────────────┐
│  Camera Status   │     │  Face Verification  │
└────────┬─────────┘     └──────────┬──────────┘
         │                          │
         ├──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
┌──────────────────┐     ┌─────────────────────┐     ┌──────────────────┐
│   Object Cues    │     │   YOLO Detections   │     │  Security Rules  │
└────────┬─────────┘     └──────────┬──────────┘     └──────────┬──────────┘
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    ▼
                     ┌─────────────────────────────┐
                     │  Multi-Modal Risk Fusion    │
                     │           Engine            │
                     └──────────────┬──────────────┘
                                    ▼
                     ┌─────────────────────────────┐
                     │ Risk: LOW / MED / HIGH /    │
                     │          CRITICAL           │
                     └─────────────────────────────┘
```

---

## 2. Core Operational Constraints & Safety Policy

To satisfy privacy, legal, and operational safeguards at Khulna University of Engineering & Technology (KUET):
* **Supporting Evidence Only**: Object detection cues (lanyard, badge, bag) are treated as supplementary evidence to evaluate general gate compliance. They do **not** prove university membership or serve as access tokens on their own.
* **Biometric Identity Limits**: The face verification module utilizes **anonymized open-source demo identities** (LFW dataset) mapped to generic tags (e.g. "Demo Member A"). It does not query or contain real KUET student biometric data.
* **Human-in-the-Loop Override**: The fusion engine outputs are purely advisory decision aids. The **human security guard** is displayed all aggregated signals and maintains the final, sole authority to allow, inspect, or deny gate access.

---

## 3. Input Signals

The engine evaluates the following input metrics dynamically inside `RiskFusionInput`:
* **Security Event Details**: The latest security rules status (`security_level` and `security_event_type`).
* **Spatial/Tracking Indicators**: Number of active tracked persons (`active_tracks`), tracks inside the gate-zone ROI (`active_tracks_in_gate_zone`), and motionless person flags (`motionless_person`).
* **Face Verification Status**: Face verification categories (`KNOWN`, `LOW_CONFIDENCE`, `UNKNOWN`, `NOT_AVAILABLE`).
* **Object Cue Status**: Local object detection status (`READY`, `DISABLED`, `MODEL_NOT_CONFIGURED`) and list of classes detected (`object_cues_detected`).
* **Environmental Context**: Temporal indicator (`after_hours`) and camera health status (`camera_available`).

---

## 4. Output Risk Levels & Decision Matrix

The engine maps inputs to a final `RiskFusionResult` containing:
* **Risk Level**: `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`.
* **Risk Score**: An integer score between `0` and `100`.
* **Reasons**: Detailed list of text reasons justifying the score and classification changes.
* **Recommended Action**: Recommended operational step for the guard.
* **Safety & Review Flags**: `human_review_required` (always `True` by default) and a standardized `privacy_note`.

### Decision Logic & Score Thresholds

| Risk Level | Score Range | Primary Conditions | Recommended Action |
| :--- | :--- | :--- | :--- |
| **LOW** | 0 - 30 | Known face, camera healthy, normal hours, no high-risk rules flagged. | Allow entry; monitor normally. |
| **MEDIUM** | 31 - 69 | Low-confidence face match, minor loitering, or missing object cues (if enabled). | Request manual ID verification. |
| **HIGH** | 70 - 84 | Unknown face in gate-zone, camera offline, motionless person during normal hours, or red security rule. | Inspect credentials and escalate query. |
| **CRITICAL** | 85 - 100 | Unknown face after-hours, motionless person after-hours, or active loitering after-hours. | Sound alert; escalate to supervisor immediately. |

### Mitigation Rules (Object Cues)
If face verification returns `UNKNOWN` or `LOW_CONFIDENCE`, the presence of verified student-associated object cues (e.g. `lanyard`, `id_card`) can act as **mitigating factors**, slightly reducing the risk score (e.g., -5 points per cue) to reduce false-alarm alerts. However, they **cannot** shift a `HIGH` or `CRITICAL` state to `LOW` without biometric/face authentication.
