# SmartKUET Sentinel: Final Demo Presentation Script (Milestone 2E)

This document outlines the official presentation scripts and demonstration flow for the SmartKUET Sentinel campus security system. All performance claims are grounded in local measurements and strictly follow system guidelines.

---

## 1. The 30-Second Elevator Pitch

> "SmartKUET Sentinel is a local-only, edge-AI security platform designed for campus gates. It integrates YOLO object detection and tracking with InsightFace biometric verification and a multi-modal risk fusion engine. By replacing opaque cloud models with local, explainable, rule-based reasoning, it flags security alerts (like loitering, after-hours breaches, and unknown entries) directly to guards in real-time. It runs entirely offline, preserving privacy, while achieving sub-12ms inference speeds locally."

---

## 2. The 2-Minute Live Demo Script

### Phase 1: Context & UI Overview (0:00 - 0:30)
* **Visual**: Show the **Showcase React Dashboard (Security Room / Landing Page)**.
* **Talking Points**:
  > "Here is our main Security Dashboard. SmartKUET Sentinel processes the live gate camera stream locally on campus. The dashboard is divided into three key panes: a live track monitor, a real-time event log, and our Explainable Multi-Modal Risk Fusion panel.
  > Notice the status indicator chips on the panel: they verify active connections to the camera, face database, object cues detection service, and active tracking system."

### Phase 2: Live Tracking & Rules Demo (0:30 - 1:00)
* **Visual**: Point to the active YOLO tracks and the green/yellow event logs (loitering/crowding).
* **Talking Points**:
  > "As people enter, the system detects and assigns unique motion tracks. If a target lingers in the defined Gate Zone ROI beyond 15 seconds, the security engine triggers a Yellow Level 'Loitering' alert, prompting the guard to verify.
  > On our local test video, this tracking pipeline achieves **98.5 FPS** with an average YOLO inference latency of **11.22 ms**, measured locally on this laptop using `sample_videos/demo.mp4`."

### Phase 3: Face Verification & Multi-Modal Fusion (1:00 - 1:40)
* **Visual**: Click on the **Guard View** to show the face matching panel and trigger the `/api/risk-fusion/status` query overrides to show state transitions.
* **Talking Points**:
  > "Our local face verification matches features against a mock LFW-based demo gallery of permitted identities.
  > Watch the Risk Fusion panel as we simulate different scenarios. When a permitted student is verified during normal hours, the risk level remains **LOW (Score: 15)**.
  > However, if an unrecognized identity is detected inside the gate zone, the fusion engine combines these signals to elevate the risk level to **HIGH (Score: 75)**, recommending a credential check. 
  > If this unrecognized entry occurs after-hours, the risk escalates to **CRITICAL (Score: 90)**, prompting a supervisor alarm.
  > All decision scoring is fully explainable, local, and advisory."

### Phase 4: Privacy & Conclusion (1:40 - 2:00)
* **Visual**: Highlight the **Privacy Notice** footer on the dashboard.
* **Talking Points**:
  > "To ensure ethical compliance, the system is strictly advisory. The final locking action always rests with a human guard. Furthermore, all biometric verification runs locally; no personal profiles are ever uploaded to the cloud or database. 
  > This is SmartKUET Sentinel: secure, local, and transparent."

---

## 3. The 5-Minute Extended Explanation

* **0:00 - 1:00**: Introduces the problem statement (security vs. privacy on campuses, latency issues with cloud APIs).
* **1:00 - 2:30**: Explains the technical architecture (YOLOv8 + ByteTrack for detection/tracking, ONNX InsightFace buffalo_s for biometric feature vectors, FastAPI router for backend orchestration).
* **2:30 - 4:00**: Highlights the math behind the Risk Fusion Engine. Explains how it operates as a deterministic state machine combining weights:
  $$\text{Score} = f(\text{Face Status}, \text{Camera Status}, \text{Gate Zone Presence}, \text{Time-of-day}, \text{Object Cues})$$
  Explain how lanyards or name badges serve as mitigation factors (subtracting 5 points) but are floored at 15 to prevent bypasses.
* **4:00 - 4:45**: Walks through the local performance benchmark: **98.5 FPS** throughput, **11.22 ms** YOLO average inference, and zero failures across the 95-test suite, measured locally on this laptop using `sample_videos/demo.mp4`.
* **4:45 - 5:00**: Emphasizes the privacy model and details next steps (fine-tuning the object cue detector with custom KUET lanyard datasets).

---

## 4. Exact Order of Pages and APIs to Show

To deliver a flawless demo, open these browser tabs in this exact order:

1. **Dashboard Page**: `http://localhost:5173/` (Security Room Dashboard showing active tracks and event streams).
2. **Guard View Page**: `http://localhost:5173/guard` (Displays biometric feed, camera parameters, and live fusion scores).
3. **Health Endpoint**: `http://127.0.0.1:8002/health`
4. **Runtime API**: `http://127.0.0.1:8002/api/runtime/status`
5. **Face Verification API**: `http://127.0.0.1:8002/api/face/status`
6. **Risk Fusion Live Endpoint**: `http://127.0.0.1:8002/api/risk-fusion/status?face_status=UNKNOWN&after_hours=true`

---

## 5. Precise Technical Terminology Guidelines

Presenters must adhere to the following terminology to ensure scientific accuracy and prevent overclaims:

* **Face Verification**: Do **NOT** refer to this as a *"KUET registry connector"*. Call it *"biometric face verification utilizing open-source demo/LFW identities (buffalo_s model)"*.
* **Object Cue Detection**: Do **NOT** claim the system actively detects badges or lanyards. Describe it as *"an integrated local code-scaffold configured for YOLOv8 object cues, currently disabled in the freeze build to await custom model training"*.
* **Risk Fusion**: Describe it as a *"deterministic, rule-based expert system providing explainable security advisory guidelines to human operators"*.
* **Performance**: State: *"Pipeline speed of 98.5 FPS and average YOLO latency of 11.22 ms, measured locally on this laptop using sample_videos/demo.mp4"*. Do not claim these are universal performance numbers.

---

## 6. How to Handle Judge Questions

### Question: "Is this database connected to real KUET students?"
* **Response**:
  > "No, the system operates entirely offline on local edge-hardware. For security and privacy compliance, we do not connect to real KUET administrative databases or store real student biometric templates. Instead, we use an open-source face gallery containing simulated demo identities for demonstration purposes."

### Question: "What if the camera is bypassed or goes down?"
* **Response**:
  > "The risk fusion engine treats camera unavailability as a high-risk event. If the camera stream goes offline, the status endpoint immediately reports a camera issue, and the fusion engine defaults to a **MEDIUM** risk level to ensure guards investigate the feed loss."

### Question: "Why did you use a deterministic fusion engine instead of an AI classifier?"
* **Response**:
  > "Campus security requires complete auditing and explainability. A deep neural network classifier for risk level is prone to hallucination and cannot explain *why* it flagged an alert. By using a deterministic rules engine that combines individual AI sensor signals (YOLO tracks, face matches), we guarantee 100% auditing transparency: guards and judges can trace the exact reasons (e.g. unrecognized face, after-hours status) behind every alarm."
