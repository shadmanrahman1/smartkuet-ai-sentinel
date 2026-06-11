# SmartKUET Sentinel - Final Submission Pack

This document compiles the project details, implemented prototype features, demo validation summary, submission checklists, and disclaimers for the KUET innovation competition.

## Project Information

*   **Project Title**: SmartKUET Sentinel: Offline Edge-AI Campus Security & Exam Integrity Assistant
*   **One-Line Pitch**: An offline-first Edge-AI computer vision assistant for campus gate monitoring and exam invigilation supporting local security guards and examiners.
*   **Repository URL**: [https://github.com/shadmanrahman1/smartkuet-ai-sentinel](https://github.com/shadmanrahman1/smartkuet-ai-sentinel)

## Problem Statement
University campus entries and exam halls require constant vigilance, yet conventional surveillance is passive, retroactively useful but failing in active prevention. Modern smart security solutions usually rely on third-party cloud-based AI. These cloud services raise major concerns:
1.  **Privacy Hazards**: Student faces, live footage, and locations are streamed off-campus to public clouds.
2.  **High Latency**: Network round-trip delays make it impossible to trigger instant gate warnings.
3.  **Dependence on Internet**: Intermittent or lost connectivity disables safety monitoring entirely.

## Proposed Solution
SmartKUET Sentinel resolves these issues by implementing a local, **offline-first Edge-AI** system. By deploying lightweight, optimized neural networks directly on campus servers or laptops, we analyze camera feeds and evaluate safety rules locally, keeping campus data completely private and securing uninterrupted operation regardless of external network connectivity.

## Implemented Prototype Features
*   **Local YOLO Object Detection**: Lightweight local model (`yolov8n.pt`) detects persons, phones, and vehicles offline.
*   **Temporary Motion Tracking**: Employs local tracking (IoU tracker backend) to count and follow targets temporarily.
*   **Deterministic Security Rules Engine**: State machine checking crowding, loitering, after-hours presence, device visibility, and camera loss to trigger color-coded alerts (Green, Yellow, Orange, Red) and action suggestions.
*   **Local Evidence Snapping**: Saves annotated JPEGs of security events locally to `snapshots/evidence/`.
*   **Interactive Web Dashboards**: Local HTML5 web pages with diagnostics, active tracking registers, incident lists, and live streams.
*   **Guard Checkpoint view**: A mobile-responsive layout for gate security guards with risk panels and control overrides.
*   **Examiner Mock hall view**: An invigilator layout tracking suspicion log tables.
*   **Tuning and Validation scripts**: Scripts (`scripts/validate_demo_video.py` and `scripts/print_demo_checklist.py`) to benchmark frames, latency metrics, and write summaries.

## Demo Validation Summary Evidence
 Tightly tuned and verified against local gate and corridor test footage (`demo.mp4`):
*   **Average YOLO CPU Inference Latency**: ~37.04 ms per frame (after lazy-loading warmup).
*   **Pipeline Processing FPS**: ~46.54 FPS.
*   **Security rule triggers**: Successfully recorded Crowd and Normal activities.
*   **Unit and Integration Testing**: 46 unit and integration tests written and passing successfully.

## Recommended Dashboard Pages to Present
*   **Central Dashboard**: `http://127.0.0.1:8002/` (Visualizes YOLO bounding boxes, tracking logs, incident updates, and hardware diagnostics).
*   **Guard View**: `http://127.0.0.1:8002/guard` (Gate risk indicator card, gate instructions, and action buttons).
*   **Examiner Mock View**: `http://127.0.0.1:8002/exam` (Seat integrity scoring, suspicious behavior explanation, and invigilator logs).

## Manual Screenshots to Capture for Proposal
1.  **Central Admin Monitor**: Open `http://127.0.0.1:8002/` with a live person in front of the camera, showcasing bounding boxes and the security level changing.
2.  **Mobile Guard Console**: Open `http://127.0.0.1:8002/guard` in a responsive phone frame showing the ALLOW/DENY/VERIFY buttons.
3.  **Invigilator Screen**: Open `http://127.0.0.1:8002/exam` showing suspicion scores.
4.  **Latest Validation Markdown**: Render and capture `runs/benchmarks/latest_validation_summary.md`.
5.  **Annotated Frame Sample**: Capture one of the exported verification JPEG frames from `runs/videos/validation_frames/`.

## Submission File Organization

### Files to Include in the Submission Repository
*   `api/` (FastAPI router endpoints)
*   `core/` (Configuration, camera stream thread, YOLO wrapper, tracker, security rules)
*   `dashboard/` (HTML structure, CSS premium dark theme styles, dynamic app JS)
*   `docs/` (Pitch, Runbook, judges Q&A, technical architecture, and final submission pack)
*   `scripts/` (Checklist, runtime check, and validation benchmarking scripts)
*   `tests/` (Static page tests, rule engine tests, camera tests)
*   `requirements.txt` & `README.md`
*   `PROJECT_CONTEXT.md`

### Files to EXCLUDE from Submission Staging (Gitignored)
*   `sample_videos/demo.mp4` (Raw video file)
*   `models/yolov8n.pt` (Lightweight model weight)
*   `runs/benchmarks/*.json` (Local validation benchmarks)
*   `runs/benchmarks/latest_validation_summary.md` (Generated benchmark summary)
*   `runs/videos/validation_frames/*.jpg` (Annotated verification frames)
*   `snapshots/evidence/*` (Local evidence captures)
*   `.venv/` (Local virtual environment)
*   `.cache/` (Pip, Torch, Ultralytics local caches)
*   `smartkuet.db` (Local SQLite database)

## Ethical & Privacy Disclaimer
> [!IMPORTANT]
> - **No Face Identification**: This prototype does not perform face identification, does not identify students, and does not conduct student profiling or facial image scanning. Student identity is not stored. It only traces temporary motion track coordinates.
> - **Human-in-the-Loop Policy**: AI only alerts operators to anomalies and blocks. It does not automatically punish, accuse, or deny entry to anyone. The final authority is strictly determined by authorized KUET guard or invigilator personnel.
> - **Local Data Governance**: All data remains entirely local. No cloud services or external APIs are used.

## Limitations & Future Scope
1.  **CPU-Only Fallback**: Inference is configured for CPU fallback by default, though optimized to run at ~35-50 FPS. Scale-out deployments will utilize CUDA-enabled laptops (e.g. RTX 3050).
2.  **Mock Invigilation Hall**: Exam integrity checks are currently mock-only. Future scope includes training a spatial-temporal action recognition model to classify cheating gestures locally.
3.  **Future Identity Verification**: Any future identity verification capability would require explicit student consent, KUET administration approval, an independent privacy review, and strictly local-only storage — with no facial data sent to any network, cloud, or third-party service.

## Final Pre-Submission Checklist
- [x] All 46 unit and integration tests pass successfully (`pytest`).
- [x] Verified `print_demo_checklist.py` outputs all checks successfully.
- [x] Verified `check_runtime.py` confirms all paths and directories exist locally.
- [x] Ensure uvicorn server has been shut down and ports `8001` and `8002` are clean.
- [x] Verify `.gitignore` is correctly configured to exclude videos, model weights, database, local snapshots, and generated JSON reports.
