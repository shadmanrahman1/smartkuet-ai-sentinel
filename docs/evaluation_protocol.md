# Evaluation Protocol — SmartKUET Sentinel

This document details the research-grade evaluation protocol for the SmartKUET Sentinel campus gate monitoring system. It outlines the metrics, datasets, evaluation methodologies, and privacy boundaries for the current prototype and future production versions.

## 1. System Components to Evaluate

The SmartKUET Sentinel pipeline consists of six primary sub-systems, each evaluated using targeted protocols:
1. **YOLO Detector**: Detects people, vehicles, and handheld devices near the gate area.
2. **Person Tracker (IoU Fallback / ByteTrack)**: Matches frame-to-frame bounding boxes to maintain identity trajectories.
3. **Security Rules Engine**: Evaluates spatial-temporal logic (gate-zone presence, loitering time, crowd thresholds).
4. **Face Verification Service**: ArcFace embedding similarity vs. the enrolled demo gallery.
5. **Object-Cue Scaffold**: Configurable auxiliary signal provider (lanyards, ID cards, visitor badges).
6. **Multi-Modal Risk Fusion Engine**: Integrates all signals deterministically to compute the fused threat level.

---

## 2. Evaluation Metrics & Protocols

> [!IMPORTANT]
> The performance metrics listed below are target benchmarks, design goals, and measurement fields. Final measured values must be filled after running the validation/benchmark scripts on the selected demo video or live camera source.

### A. Performance & Efficiency Targets (Vitals)
* **Frames Per Second (FPS) target**: The overall throughput of the video processor thread.
  * *Protocol*: Measured frame rate of the live processor loop over a 60-frame moving window.
  * *Target Goal*: $\ge 30$ FPS (live feed rate) on standard edge hardware (e.g. CPU or RTX Laptop GPU).
* **Average Inference Latency Targets (ms)**:
  * *YOLO Latency Goal*: Time taken for object detection model forward pass. Target Goal: $\le 15$ ms.
  * *Face Embed Latency Goal*: Time taken to generate the 512-dim ArcFace embedding vector. Target Goal: $\le 20$ ms.
  * *Face Match Latency Goal*: Search time inside the database gallery. Target Goal: $\le 5$ ms.

### B. Integration & API Health Targets
* **API Response Health Target**: Standard response code and latency profiles.
  * *Metric*: Latency (ms) of `/api/runtime/status` and `/api/risk-fusion/status`.
  * *Target Goal*: 100% status code `200` OK under normal operation, average response time $\le 10$ ms.
* **WebSocket Payload Integrity Target**: Real-time broadcast delay of security incidents.
  * *Metric*: Transmission delay (ms) from event detection to client rendering. Target Goal: $\le 200$ ms.

### C. Algorithmic Correctness
* **Risk Fusion Logic Validation**: Matches the output level (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) and score (0-100) against the design matrix.
  * *Protocol*: Evaluated via automated unit tests mapping standard and edge-case permutations (e.g. unknown face + gate zone presence + after-hours must yield `CRITICAL`).
* **Face Verification Similarity Statistics**:
  * *Cosine Similarity Threshold*: Threshold set to $\ge 0.40$ for `KNOWN` matches and $[0.30, 0.40)$ for `LOW_CONFIDENCE`.
  * *Metrics*: False Acceptance Rate (FAR) and False Rejection Rate (FRR) evaluated on verification test runs.
* **Object-Cue Mitigation Accuracy**:
  * *Protocol*: Checks score deduction bounds. A present lanyard/ID card reduces the score by exactly $5$ points, but score floors (UNKNOWN = 50, LOW_CONFIDENCE = 30) must hold.

---

## 3. Dataset Roles & Reference Frameworks

To maintain an offline, local-only edge posture, the system splits data roles as follows:

| Dataset | Role in Prototype | Reference Target (Future Work) |
| :--- | :--- | :--- |
| **Labeled Faces in the Wild (LFW)** | Enrolls mock gallery members ("Demo Member A/B/C") for face verification without using real student data. | Local KUET student registration database (fully encrypted and offline). |
| **Roboflow Universe / SHWD / COCO** | Defines research baseline anchors (lanyard, name badge, ID card, helmet) for local YOLO-scaffold class detection. | Custom-annotated KUET gate dataset for domain-specific fine-tuning. |
| **Local Camera / Video Feed** | Loop-playing validation videos (`sample_videos/demo.mp4`) used for offline performance benchmarking. | Live CCTV camera RTSP streams at the KUET gate. |

---

## 4. Current Capacity vs. Future Work

### Evaluated in Current Prototype
* YOLO CPU/GPU inference latency and throughput.
* IoU tracker fallback speed and ghost track pruning.
* Cooldown logic effectiveness under continuous loitering conditions.
* Cosine similarity comparison correctness on small-resolution upscaled faces.
* Multi-modal risk score logic correctness across all 95 automated test cases.

### Future Implementation & Evaluation
* Fine-tuning a unified YOLOv8/v11 model on campus object cues to reduce CPU footprint.
* Closed-loop hardware acceleration profiling on dedicated edge-compute hardware (e.g. NVIDIA Jetson).
* Cross-camera track matching (re-identification) between entrance and exit gates.

---

## 5. Limitations & Ethical Constraints

* **Advisory Only**: Fused risk scores are advisory helper signals for the security staff. The system **does not automate gate lockouts** or restrict physical access without manual guard confirmation.
* **Biometric Integrity**: The prototype operates entirely locally. Face embeddings are stored as `.npy` cache files on the local disk. No student faces or biometric signatures are stored on third-party cloud servers or exposed to external APIs.
* **Academic/Demo Boundaries**: All demo identities use public-domain LFW academic datasets. No real student records or personal identifiable information (PII) are queried or held in the local database.
