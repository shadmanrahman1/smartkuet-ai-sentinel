# SmartKUET Sentinel: Measured Validation Snapshot & Performance Freeze (Milestone 2E)

This document provides a measured validation snapshot of the SmartKUET Sentinel system as of Milestone 2E Phase 2. All metrics and results listed here are verified and measured on a local development machine. No mock values or overclaims are included.

## System Metadata
* **Branch Checked**: `milestone-2e-evaluation-pack`
* **Latest Commit Checked**: `01a5022 docs: add evaluation and presentation pack`
* **Verification Environment**: 
  - **OS**: Windows 11 (10.0.26200)
  - **Python**: `3.13.5`
  - **CUDA/GPU**: Available (1 device: `NVIDIA GeForce RTX 3050 Laptop GPU`, CUDA `12.8`)
  - **PyTorch**: `2.11.0+cu128` (CUDA-enabled)
  - **OpenCV**: `4.13.0`

---

## 1. Test Suite Results
* **Command run**: `.venv\Scripts\python -m pytest --tb=short -q`
* **Result**: **95 Passed, 0 Failed** (15 warnings, mainly related to `TestClient` and `onnxruntime` CUDA providers fallback in standard library checks)
* **Execution Time**: ~32.0 seconds

---

## 2. React Showcase Frontend Build
* **Command run**: `npm run build --prefix showcase-frontend`
* **Status**: **Successful** (Vite build completed in `173ms`)
* **Generated Assets**:
  - `showcase-frontend/dist/index.html` (0.72 kB)
  - `showcase-frontend/dist/assets/index-DbnyrEPT.css` (8.13 kB)
  - `showcase-frontend/dist/assets/index-cfN_EKyF.js` (240.24 kB)

---

## 3. Backend API Smoke Test Results
The FastAPI backend (`api.main:app`) was initialized and queried locally on port `8002`.

| Endpoint | HTTP Status | Key Response JSON Fields | Details / Notes |
| :--- | :--- | :--- | :--- |
| `/health` | `200` | `{"status": "ok", "app": "SmartKUET Sentinel"}` | Basic server diagnostic OK |
| `/api/runtime/status` | `200` | `yolo_model_exists`, `cuda_available`, `tracking_enabled`, `directories` | Confirms GPU, models, and outputs directories are active and configured |
| `/api/security/status` | `200` | `rules_enabled`, `latest_events`, `latest_level`, `cooldowns` | Confirms normal hours (6-22), Gate Zone bbox, and loitering settings are active |
| `/api/face/status` | `200` | `model_loaded`, `gallery_size`, `gallery_members` | Buffalo_s loaded with 3 members: `DemoMemberA`, `DemoMemberB`, `DemoMemberC` |
| `/api/object-cues/status` | `200` | `status`: `"DISABLED"`, `supported_cues`, `configured` | Scaffold is active but detection is currently disabled in configuration |
| `/api/risk-fusion/status` | `200` | `level`: `"MEDIUM"`, `score`: `30`, `human_review_required`: `true` | Defaults to Medium Risk because no face is in camera view / camera is offline |

---

## 4. Multi-Modal Risk Fusion Scenario Results
Below are the responses returned by the risk fusion engine `/api/risk-fusion/status` under query parameter overrides.

| Scenario / Query Parameters | HTTP Status | Risk Level | Risk Score | Reasons Count | Recommended Action | Human Review Required | Privacy Note Exists |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| `face_status=KNOWN`<br>`camera_available=true`<br>`after_hours=false` | `200` | `LOW` | `15` | `1` | `Allow entry; monitor normally.` | `Yes` (True) | **Yes** |
| `face_status=UNKNOWN`<br>`active_tracks_in_gate_zone=1` | `200` | `HIGH` | `75` | `2` | `Inspect credentials and escalate query.` | `Yes` (True) | **Yes** |
| `face_status=UNKNOWN`<br>`after_hours=true` | `200` | `CRITICAL` | `90` | `3` | `Sound alert; escalate to supervisor immediately.` | `Yes` (True) | **Yes** |

> [!NOTE]
> * **Privacy Notice Verification**: All risk fusion outputs contain a mandatory footer stating: *"Privacy Notice: The risk fusion engine runs locally. Open-source demo identities only. No real student biometric profiles are queried or stored."*
> * **Human Review Required**: All decisions remain advisory (`human_review_required: true`), preserving human-in-the-loop control.

---

## 5. Local Video Performance Benchmark
* **Source Video**: `sample_videos/demo.mp4`
* **Warmup Frames**: `5`
* **Benchmark Duration**: `20 seconds` (entire video parsed)
* **Results (Measured Locally)**:
  - **Processed Frames**: `199`
  - **Approximate Speed**: **98.5 FPS** (Measured locally on this laptop using sample_videos/demo.mp4)
  - **Average Inference Time (YOLO)**: **11.22 ms** (Measured locally on this laptop using sample_videos/demo.mp4; warmup first-frame latency: `25.46 ms`)
  - **Average Person Count**: `0.69` (Max active tracks in frame: `8`)
  - **Total Tracks Seen**: `39`
  - **Event Logs generated**: `124` (123 `NORMAL_ACTIVITY` green level, 1 `CROWDING` yellow level)
  - **Highest Security Level Emitted**: `YELLOW`

---

## 6. Project Files Ignored (Not Committed)
The following directories and files are actively ignored in the git tree to keep the repository clean of large binaries and runtime artifacts:
* `showcase-frontend/dist/`
* `showcase-frontend/node_modules/`
* `.venv/`
* `models/` (model weights)
* `.cache/` (model downloads cache)
* `runs/benchmarks/*.json` (raw local logs)
* `runs/videos/validation_frames/` (test frames)
* `smartkuet.db` (local development SQLite state)

---

## 7. Performance & Claim Boundaries

### Allowed Presentation Claims
1. **Explainable Deterministic Fusion**: A multi-modal rule engine combines YOLO tracks, gate-zone ROI violations, schedule time, and face verification outputs to produce a structured security response.
2. **Sub-15ms Detection Latency**: YOLO detection and tracking averages `11.22 ms` per frame (Measured locally on this laptop using sample_videos/demo.mp4).
3. **High-Speed Throughput**: Local processing of a 1080p stream achieves **98.5 FPS** (Measured locally on this laptop using sample_videos/demo.mp4).
4. **Mock Identity Verification**: Employs an open-source face verification model (buffalo_s) against a pre-registered local gallery of simulated identities.

### Disallowed Claims (Do NOT Claim)
1. **Live KUET Database Connection**: The system does **not** link to any real KUET student identity directory or administrative databases.
2. **Autonomous Physical Locking**: The fusion engine is advisory only and does not control gate locks directly without human approval.
3. **Active Custom Object Cue Analysis**: Object cues (ID cards, lanyards) are implemented as a code-scaffold but are currently **disabled** in the freeze package (no active trained weights loaded).

---

## 8. Next Recommended Actions
1. **Field Video Captures**: Record real-world high-resolution gate activity streams at KUET to evaluate tracker durability under backlight or extreme weather.
2. **Object Cue Custom Model Training**: Collect and label images of actual KUET lanyards, lanyards with cards, and badges, then train the scaffold YOLO model.
3. **Integration with Relays**: Prototype hardware controllers (Raspberry Pi/Arduino relays) to receive API alerts and act on gate triggers.
