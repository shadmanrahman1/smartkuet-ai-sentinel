# SmartKUET Sentinel Project Context

This file is the running Codex work log for this project. Each time Codex works on the project, update this file with what changed, why it changed, and the current project context needed for the next session.

## Current Context

- Project folder: `F:\Skill_WORK\CODE\SMART_KUET_Innovative`
- Project name: SmartKUET Sentinel
- Current milestone: Milestone 2E Research Evaluation & Competition Presentation Pack (branch: milestone-2e-evaluation-pack)
- Runtime target: local/offline deployment from the project drive
- Important constraint: keep project runtime files, cache, virtual environment, database, snapshots, and sample videos inside this project folder/local drive. Avoid using `C:` for project configuration or runtime artifacts.
- Frontend stack (production/fallback): plain HTML, local CSS, and vanilla JavaScript in `dashboard/`. Routes `/`, `/guard`, `/exam` served directly by FastAPI. Always works offline.
- Frontend stack (optional showcase): Vite + React in `showcase-frontend/`. Runs on port 5173. Uses Vite dev proxy to forward `/api` to FastAPI on port 8002. `node_modules/` and `dist/` are gitignored. No Next.js.
- Backend stack: FastAPI, Uvicorn, OpenCV, SQLite, WebSockets, Ultralytics YOLO, Torch, InsightFace.
- YOLO is included for object/person detection, tracking, and security event rules. InsightFace is included for local face verification vs LFW demo gallery. No MediaPipe, exam behavior scoring, training, or cloud APIs yet.
- Milestone 2C adds local-only object cue detection scaffolding (ID-card, lanyard, visitor badge, bag, helmet) with supporting security-risk signals.


## Current Implementation

- FastAPI app lives in `api/main.py`.
- Configuration lives in `core/config.py`.
- SQLite helper lives in `core/database.py`.
- Camera/video abstraction lives in `core/camera.py`.
- YOLO detector wrapper lives in `core/detector.py`.
- Security event rules live in `core/security_rules.py`.
- Camera plus detector background processing lives in `core/video_processor.py`.
- Person tracking lives in `core/tracker.py`; current backend is `iou_fallback` while `TRACKER_TYPE=bytetrack` remains the requested/default config.
- Mock security worker lives in `workers/security_worker.py`.
- Mock exam worker lives in `workers/exam_worker.py`.
- Dashboard pages live in `dashboard/`.
- Tests live in `tests/`.
- Project-local setup helper lives in `scripts/local_env.ps1`.
- YOLO model path defaults to `models/yolov8n.pt`.
- Project-local cache paths are set for pip, Python bytecode, Ultralytics, Torch, XDG cache, and Matplotlib.
- Runtime diagnostics are available at `/api/runtime/status`, `/api/camera/status`, and `/api/video/status`.
- Tracking status is available at `/api/tracking/latest`; tracker reset is available at `POST /api/tracking/reset`.
- Security rules status is available at `/api/security/status`; rule cooldown reset is available at `POST /api/security/rules/reset`.
- Evidence snapshots are saved through `POST /api/evidence/snapshot` into `snapshots/evidence/`.
- Runtime check script: `python scripts/check_runtime.py`.
- YOLO benchmark script: `python scripts/benchmark_yolo.py --source sample_videos/demo.mp4 --seconds 20`; it now includes tracking and security-rule metrics.
- Standing cleanup rule: after Codex finishes project work, stop SmartKUET Uvicorn/Python server processes and verify SmartKUET ports such as `8001` and `8002` no longer respond, unless the user explicitly asks to leave the server running.

## Work Log

### 2026-06-07 - Milestone 0 Foundation

Completed the initial SmartKUET Sentinel foundation.

- Created the project structure for API, core modules, workers, dashboards, tests, snapshots, sample videos, data, and scripts.
- Implemented FastAPI routes for `/`, `/guard`, `/exam`, `/health`, `/api/persons`, `/api/security/incidents`, `/api/exam/events`, and `/api/video_feed`.
- Added WebSocket routes `/ws/security` and `/ws/exam` with mock real-time events.
- Implemented SQLite tables for `persons`, `security_incidents`, and `exam_events`.
- Added a threaded OpenCV `CameraStream` abstraction for webcam, video file, or IP camera sources.
- Added local dashboard pages for central monitoring, guard workflow, and examiner workflow.
- Used local CSS instead of Tailwind CDN so the app does not depend on runtime internet.
- Added `.env.example`, `.gitignore`, `requirements.txt`, tests, and README setup notes.
- Created a project-local `.venv` and `.cache` during setup.
- Verified tests with `pytest`: `4 passed, 1 warning`.
- Started Uvicorn on `http://127.0.0.1:8001` because port `8000` was already occupied.

### 2026-06-07 - Project Context Log

Added this `PROJECT_CONTEXT.md` file as the single project-local Codex work log.

- Going forward, update this file whenever Codex works on the project.
- Add new entries under `Work Log`.
- Keep `Current Context` accurate when project constraints, architecture, ports, dependencies, or milestone scope change.

### 2026-06-07 - Milestone 1A YOLO Detection Foundation

Added the YOLO detection foundation while keeping the scope limited to object/person detection.

- Added `core/detector.py` with a lazy-loading `YOLODetector` wrapper.
- Added `core/video_processor.py` to combine `CameraStream` with YOLO detection and annotated frames.
- Updated `core/config.py` with YOLO settings, project-local path settings, and `ensure_project_dirs()`.
- Updated `api/main.py` to initialize the camera/video processor, serve annotated MJPEG when enabled, expose `/api/detections/latest`, and include `detection_summary` in `/ws/security` events.
- Updated `dashboard/index.html`, `dashboard/guard.html`, `dashboard/app.js`, and `dashboard/styles.css` with person, phone, vehicle, total object, and YOLO status displays.
- Updated `.env.example`, `.gitignore`, `requirements.txt`, `scripts/local_env.ps1`, and `README.md`.
- Added `models/.gitkeep` and `runs/.gitkeep`.
- Added tests in `tests/test_detector_summary.py` and `tests/test_config_paths.py`. These tests do not download or load the YOLO model.

Dependencies added:

- `ultralytics`
- `torch`
- `torchvision`

Local dependency install result:

- Installed the updated requirements into `.venv`.
- Pip cache was forced to `.cache\pip`.
- Torch installed as CPU-only: `torch 2.12.0+cpu`, `cuda_available False`, `cuda_version None`.
- `models/yolov8n.pt` downloaded successfully into the project-local `models/` folder.

Verification:

- `pytest`: `7 passed, 1 warning`.
- Fresh Uvicorn verification succeeded on `http://127.0.0.1:8002`.
- `/health` returned `{"status":"ok","app":"SmartKUET Sentinel"}`.
- `/api/detections/latest` returned enabled summary JSON with zero counts and `Waiting for camera frame`.
- `/api/video_feed` returned `200` with `multipart/x-mixed-replace; boundary=frame`.
- `/`, `/guard`, `/exam`, and `/dashboard/styles.css` returned `200`.

Known limitations:

- Port `8001` still had stale old Uvicorn listeners during verification, so the fresh app was verified on `8002`.
- The local camera was not providing usable frames during verification, so detection counts stayed at zero.
- OpenCV logged MSMF camera grab warnings while trying to read the default webcam source.
- CUDA is not available with the currently installed Torch build. Use a CUDA-enabled Torch build later if GPU inference is needed.
- Face recognition, ByteTrack tracking, InsightFace, MediaPipe, exam behavior scoring, and model training are still intentionally not implemented.

### 2026-06-07 - Stopped Local SmartKUET Servers

Stopped the SmartKUET Uvicorn/Python processes that were serving this project.

- Stopped the active SmartKUET server on port `8002`.
- Found two orphaned Python child processes from earlier Uvicorn reload runs and stopped them.
- Verified `http://127.0.0.1:8001/health` no longer responds.
- Verified `http://127.0.0.1:8002/health` no longer responds.
- Left port `8000` running because it belongs to a different project: `halal-ai-trading-assistant`.

### 2026-06-07 - Milestone 1B Stable Video Input and Diagnostics

Added stable video input, runtime diagnostics, YOLO benchmarking, and evidence capture.

- Updated `core/config.py` with `CAMERA_RECONNECT_SECONDS`, `CAMERA_LOOP_VIDEO`, `BENCHMARK_OUTPUT_DIR`, `EVIDENCE_DIR`, `VIDEO_OUTPUT_DIR`, expanded project directory creation, and `get_runtime_info()`.
- Reworked `core/camera.py` to classify webcam, video file, IP camera, RTSP, and unknown sources; reconnect failed sources; loop local video files; track frame count, resolution, FPS estimate, and last error.
- Updated `core/detector.py` with `auto` device selection, CPU fallback when CUDA is unavailable, selected-device reporting, and `get_status()`.
- Reworked `core/video_processor.py` with fallback camera frame generation, inference timing, processed frame count, effective FPS, model error reporting, selected device tracking, latest summary, status reporting, and annotated-frame saving.
- Updated `api/main.py` with `/api/runtime/status`, `/api/camera/status`, `/api/video/status`, and `POST /api/evidence/snapshot`.
- Updated `dashboard/index.html`, `dashboard/guard.html`, `dashboard/app.js`, and `dashboard/styles.css` with runtime diagnostics and a Save Evidence Snapshot button.
- Added `scripts/check_runtime.py` and `scripts/benchmark_yolo.py`.
- Added `sample_videos/README.md`, `runs/benchmarks/.gitkeep`, `runs/videos/.gitkeep`, and `snapshots/evidence/.gitkeep`.
- Updated `.env.example`, `.gitignore`, `scripts/local_env.ps1`, `README.md`, and tests.

Tests and diagnostics:

- `pytest`: `13 passed, 1 warning`.
- `python scripts/check_runtime.py` confirmed Python `3.13.5`, OpenCV `4.13.0`, Torch `2.12.0+cpu`, CUDA unavailable, Ultralytics available, YOLO model exists, and all project runtime directories exist.
- `python scripts/benchmark_yolo.py --source sample_videos\demo.mp4 --seconds 2` handled the missing sample video gracefully, wrote a JSON report under `runs/benchmarks/`, and reported `Could not open source`.
- Fresh Uvicorn verification succeeded on `http://127.0.0.1:8002`.
- `/health` returned `{"status":"ok","app":"SmartKUET Sentinel"}`.
- `/api/runtime/status` returned combined runtime, camera, video processor, and detection status.
- During verification, the webcam opened successfully at `640x480`, selected YOLO device was `cpu`, CUDA was unavailable, and the detector processed frames.
- `POST /api/evidence/snapshot` saved `snapshots\evidence\snapshot_20260607_100030_467650.jpg`.
- `/api/video_feed` returned `200` with `multipart/x-mixed-replace; boundary=frame`.
- `/`, `/guard`, `/exam`, and `/dashboard/styles.css` returned `200`.

Known limitations:

- Torch is still CPU-only, so RTX 3050 acceleration is not active.
- No real CCTV/sample video has been placed in `sample_videos/` yet; benchmark success with a video file needs a local demo video.
- Detection counts were zero during the live webcam check.
- The app was verified on `http://127.0.0.1:8002`; port `8000` belongs to `halal-ai-trading-assistant`.
- ByteTrack remains the recommended next milestone, but it is not implemented yet.

### 2026-06-07 - Post-Work Cleanup Rule and Port Shutdown

Added a standing cleanup rule for future Codex work on this project.

- After project work finishes, stop SmartKUET Uvicorn/Python server processes.
- Verify SmartKUET ports such as `8001` and `8002` no longer respond.
- Leave unrelated local servers alone unless explicitly asked; port `8000` previously belonged to `halal-ai-trading-assistant`.
- Stopped the SmartKUET server that was running on `8002`.
- Verified `http://127.0.0.1:8001/health` no longer responds.
- Verified `http://127.0.0.1:8002/health` no longer responds.

### 2026-06-07 - Milestone 1C Person Tracking Foundation

Added person tracking on top of the YOLO detection pipeline while keeping the scope limited to temporary track IDs.

- Added tracking config in `core/config.py`: `TRACKING_ENABLED`, `TRACKER_TYPE`, `TRACK_PERSON_CLASS_NAME`, `TRACK_CONF`, `TRACK_IOU`, `MAX_TRACK_AGE_SECONDS`, and `TRACKING_OUTPUT_DIR`.
- Added `core/tracker.py` with `TrackState`, `PersonTracker`, and IoU matching via `bbox_iou()`.
- Integrated tracking into `core/video_processor.py` so person tracks are updated after detections and annotated video shows labels like `ID 3 | person | 0.82`.
- Kept existing detection summaries for phones, vehicles, and total objects.
- Updated `api/main.py` with `GET /api/tracking/latest`, `POST /api/tracking/reset`, tracking in `/api/runtime/status`, and `tracking_summary` in `/ws/security` events.
- Updated `dashboard/index.html`, `dashboard/guard.html`, `dashboard/app.js`, and `dashboard/styles.css` with tracking panels, active track IDs, track ages, and a Reset Tracker button.
- Extended `scripts/benchmark_yolo.py` with tracking metrics: tracking enabled, tracker type, average active tracks, max active tracks, and total tracks seen.
- Updated `scripts/check_runtime.py` with tracking config output.
- Updated `.env.example`, `.gitignore`, `scripts/local_env.ps1`, `README.md`, and tests.
- Added `runs/tracking/.gitkeep`.

Tests and diagnostics:

- `pytest`: `19 passed, 1 warning`.
- `python scripts/check_runtime.py` confirmed Torch `2.12.0+cpu`, CUDA unavailable, Ultralytics available, YOLO model exists, `TRACKING_ENABLED=True`, `TRACKER_TYPE=bytetrack`, and `runs/tracking` exists.
- `python scripts/benchmark_yolo.py --source sample_videos\demo.mp4 --seconds 10` handled the missing sample video gracefully, wrote a JSON report under `runs/benchmarks/`, and reported `Could not open source`.
- Fresh Uvicorn verification succeeded on `http://127.0.0.1:8002`.
- `/health` returned `{"status":"ok","app":"SmartKUET Sentinel"}`.
- `/api/tracking/latest` returned enabled tracking JSON with `tracker_type=iou_fallback`, requested tracker `bytetrack`, zero active tracks, and zero total tracks seen.
- `/api/runtime/status` included runtime, camera, video processor, detections, and tracking status.
- `POST /api/tracking/reset` returned `{"reset": true, ...}`.
- `/api/video_feed` returned `200` with `multipart/x-mixed-replace; boundary=frame`.
- `/`, `/guard`, `/exam`, `/dashboard/app.js`, and `/dashboard/styles.css` returned `200`.

Known limitations:

- Current tracker backend is `iou_fallback`, not full Ultralytics ByteTrack integration.
- Track IDs are temporary and do not identify people.
- No face recognition has been added.
- Torch is still CPU-only, so RTX 3050 acceleration is not active.
- No `sample_videos/demo.mp4` exists yet, so video-file benchmark still reports `Could not open source`.
- Live webcam verification produced zero active tracks because no person detections were present.
- Next recommended milestone: Milestone 1D, security event logic from tracking plus object cues. Face recognition should still wait.

### 2026-06-07 - Git Repository Initialized and Published

Initialized Git for the local project and pushed it to GitHub.

- Ran `git init` and set the branch to `main`.
- Added remote `origin` as `https://github.com/shadmanrahman1/smartkuet-ai-sentinel.git`.
- Tightened `.gitignore` before staging so generated runtime files stay out of version control.
- Ignored `.venv/`, `.cache/`, `.pytest_cache/`, `smartkuet.db`, `models/yolov8n.pt`, generated benchmark JSON, generated evidence snapshots, and future generated run outputs.
- Created initial commit `787f778` with message `Initial SmartKUET Sentinel implementation`.
- Pushed `main` to `origin/main`.

### 2026-06-07 - Milestone 1D Security Event Rules Engine

Added deterministic security event rules using real detection, tracking, camera, and time signals.

- Added `core/security_rules.py` with `SecurityEvent`, `SecurityRulesEngine`, cooldown reset/status helpers, event copying, and highest-level event selection.
- Added rules for `NORMAL_ACTIVITY`, `CROWDING`, `LOITERING`, `PHONE_VISIBLE_AT_GATE`, `VEHICLE_NEAR_ENTRY`, `CAMERA_UNAVAILABLE`, `AFTER_HOURS_ACTIVITY`, and `HIGH_RISK_COMBINED`.
- Added security rule config in `core/config.py` and `.env.example`: `SECURITY_RULES_ENABLED`, normal hours, crowding threshold, loiter threshold, event cooldowns, security location, and snapshot toggle.
- Integrated the rules engine into `core/video_processor.py` so the background loop evaluates security status after camera, detection, and tracking updates.
- Added yellow/orange/red incident logging to the existing SQLite `security_incidents` table through the existing DB schema.
- Added optional generated event snapshots under `snapshots/evidence/security_event_YYYYMMDD_HHMMSS.jpg`.
- Added `get_security_status()` and `reset_security_rules()` to the video processor.
- Updated `api/main.py` with `GET /api/security/status`, `POST /api/security/rules/reset`, security status inside `/api/runtime/status`, and rules-engine security websocket payloads.
- Kept the old mock security websocket path only as fallback when the rules engine is unavailable or disabled.
- Updated the central dashboard with a Security Rules Panel showing current level, event type, instruction, related track IDs, active tracks, phones, vehicles, thresholds, after-hours state, evidence summary, recent color-coded events, and a cooldown reset button.
- Updated the guard page to prioritize the real rule instruction, event type, level, related track IDs, and evidence summary while keeping local ALLOW, DENY, and VERIFY ID actions.
- Extended `scripts/benchmark_yolo.py` with security metrics: `security_rules_enabled`, `event_count_by_type`, `event_count_by_level`, `total_security_events`, and `highest_level_seen`.
- Extended `scripts/check_runtime.py` with security rule configuration output.
- Updated `README.md` with Milestone 1D scope, rule descriptions, new endpoints, controls, benchmark metrics, troubleshooting, and next milestone guidance.
- Added tests for rule behavior, cooldowns, `/api/security/status`, `/api/security/rules/reset`, and `/api/runtime/status` security shape.

Tests and diagnostics:

- `pytest`: `29 passed, 1 warning`.
- `python scripts/check_runtime.py` confirmed Python `3.13.5`, OpenCV `4.13.0`, Torch `2.12.0+cpu`, CUDA unavailable, Ultralytics available, YOLO model exists, tracking config, security config, and all project runtime directories exist.
- `python scripts/benchmark_yolo.py --source sample_videos\demo.mp4 --seconds 2` handled the missing sample video gracefully, wrote a JSON report under `runs/benchmarks/`, included security metrics, and reported `Could not open source`.
- Fresh Uvicorn verification succeeded on `http://127.0.0.1:8002` with `CAMERA_SOURCE=tests/no-camera.mp4` for deterministic no-camera checks.
- `/health` returned `{"status":"ok","app":"SmartKUET Sentinel"}`.
- `/api/security/status` returned `rules_enabled=true`, `latest_level=red`, `latest_event_type=HIGH_RISK_COMBINED`, and instruction `Escalate to the security supervisor.` because the test camera source was unavailable.
- `/api/security/status` also returned `CAMERA_UNAVAILABLE` and `HIGH_RISK_COMBINED` events with evidence showing `camera_is_opened=false`, `camera_frame_count=0`, zero tracks, zero phones, and zero vehicles.
- `/api/runtime/status` included `security_status` with the same red high-risk camera-unavailable state.
- `POST /api/security/rules/reset` returned `{"reset": true, ...}`.
- `/`, `/guard`, `/exam`, `/dashboard/app.js`, and `/dashboard/styles.css` returned `200`.
- After verification, the temporary SmartKUET server was stopped and both `http://127.0.0.1:8001/health` and `http://127.0.0.1:8002/health` no longer responded.

Known limitations:

- The rules depend on current YOLO detections, temporary track IDs, and camera availability; they do not identify people.
- Current tracker backend is still `iou_fallback`, not full Ultralytics ByteTrack integration.
- No face recognition, InsightFace, MediaPipe, exam behavior scoring, model training, or cloud APIs were added.
- Torch is still CPU-only, so RTX 3050 acceleration is not active.
- No `sample_videos/demo.mp4` exists yet, so video-file benchmark still reports `Could not open source`.
- Security thresholds are defaults and should be tuned with real KUET gate footage.
- Next recommended milestone: Milestone 2A, start the face detection and identity foundation after tuning validation passes successfully. Face recognition should still wait for baseline approval.

### 2026-06-11 - Milestone 1E Validation and Tuning

Validated and tuned the YOLO + tracking + security rules pipeline and added demo-readiness resources.

- Added settings loading for `DEMO_PROFILE` in [core/config.py](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/core/config.py) and default demo profile options to [.env.example](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/.env.example).
- Created [scripts/print_demo_checklist.py](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/scripts/print_demo_checklist.py) to check local files (demo video, YOLO model), CUDA status, directory presence, and list setup commands.
- Created [scripts/validate_demo_video.py](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/scripts/validate_demo_video.py) which runs the pipeline frame-by-frame and exports performance and security metrics to `runs/benchmarks/validation_YYYYMMDD_HHMMSS.json` and 3 annotated frames to `runs/videos/validation_frames/`.
- Updated [README.md](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/README.md) with sections on sample videos, running the validation script, JSON formatting, annotated frames, track limitations, and human security guard final control.
- Added tests in [tests/test_demo_checklist_script.py](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/tests/test_demo_checklist_script.py), [tests/test_validate_demo_video_missing_source.py](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/tests/test_validate_demo_video_missing_source.py), and [tests/test_validation_report_shape.py](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/tests/test_validation_report_shape.py).

Tests and diagnostics:

- `pytest` passed 32 tests (3 new tests added).
- Verified `scripts/print_demo_checklist.py` outputs all checks correctly.
- Gracefully handled missing source video inside the validation script with helpful user instructions.

Known limitations:

- The system still runs on CPU fallback only because CUDA is not installed in local PyTorch.
- Demo video must be added by the user manually to `sample_videos/demo.mp4`.
- Track IDs are temporary and do not identify specific students.


### 2026-06-11 - Milestone 1F Demo Polish and Validation Fixes

Polished the demo validation reporting, added warmup filters, dynamic frame saving, and attribution/privacy guidelines.

- Updated [scripts/validate_demo_video.py](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/scripts/validate_demo_video.py) with `--warmup-frames` option to exclude lazy-loading latency and compute clean `average_inference_ms_after_warmup` and `average_inference_ms_all` metrics.
- Added dynamic buffering in the validation script to guarantee exactly 3 evenly spaced annotated frames are written as `validation_sample_1.jpg`, `validation_sample_2.jpg`, and `validation_sample_3.jpg` based on actual processed progress.
- Added `--write-summary` option to output proposal-ready summary markdown `runs/benchmarks/latest_validation_summary.md`.
- Created [sample_videos/ATTRIBUTION.md](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/sample_videos/ATTRIBUTION.md) to provide license attributes and privacy guidelines for validation videos.
- Updated [.gitignore](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/.gitignore) to exclude large demo video formats while keeping documentation.
- Updated [scripts/print_demo_checklist.py](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/scripts/print_demo_checklist.py) with warning reminders and updated command flags.
- Updated [README.md](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/README.md) with sections on privacy, video attribution, and temporary ID disclaimers.
- Updated tests in [tests/test_validation_report_shape.py](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/tests/test_validation_report_shape.py) and added new tests [tests/test_attribution_exists.py](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/tests/test_attribution_exists.py) and [tests/test_gitignore_ignores_videos.py](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/tests/test_gitignore_ignores_videos.py).

### 2026-06-11 - Milestone 1G Demo UI and Submission Screenshot Polish

Polished the design aesthetics, layouts, and documentation to make the dashboard screens screenshot-ready for the proposal.

- Overwrote [dashboard/styles.css](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/dashboard/styles.css) with a dark theme design system incorporating glassmorphism, gradient text headers, responsive padding, HSL status indicators (green, yellow, orange, red), and custom hover/focus transition dynamics.
- Polished [dashboard/index.html](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/dashboard/index.html) with "SmartKUET Sentinel" branding subtitle, a demo status strip showing offline claims, "Live annotated video feed" canvas labels, and the central Human-in-the-Loop policy disclaimer.
- Re-styled [dashboard/guard.html](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/dashboard/guard.html) as a mobile-first decision assistant with enlarged status cards, gate action buttons (ALLOW, VERIFY ID, DENY), and helper disclaimers.
- Refactored [dashboard/exam.html](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/dashboard/exam.html) mock page with suspicion score cards, suspicion level index references, and action overrides.
- Updated [dashboard/app.js](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/dashboard/app.js) to append dynamic text state formatting and clear out WebSocket placeholders ("No recent security events", "Waiting for live data...") when messages are received.
- Created [docs/demo_runbook.md](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/docs/demo_runbook.md) runbook with exact setup checklists, commands, browser URLs, and screenshot points.
- Created [docs/submission_pitch.md](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/docs/submission_pitch.md) containing the official innovation proposal pitch, offline edge-AI flow architecture, and current prototype capacities.
- Added tests in [tests/test_demo_docs_exist.py](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/tests/test_demo_docs_exist.py) and [tests/test_dashboard_static_content.py](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/tests/test_dashboard_static_content.py).

Tests and diagnostics:

- `pytest` passed successfully with 37 tests (2 new static content/doc tests added).
- Verified local styles, cards, and disclaimers are correctly served.

Known limitations:

- The system runs on CPU fallback locally unless GPU CUDA-enabled PyTorch is configured.
- Invigilation scoring and student identity checking remain mock/future signals.
- Security thresholds must be calibrated with live KUET gate footage.

Next recommended milestone:

- Milestone 1H: Final Submission Asset Pack — screenshots, demo summary, proposal PDF/README polish, and final repository cleanup.

### 2026-06-11 - Milestone 1H Final Submission Asset Pack

Prepared and structured the final submission-ready documentation pack for the KUET innovation competition.

- Created [docs/final_submission_pack.md](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/docs/final_submission_pack.md) as the central repository details, features list, validation highlights, and privacy checklists document.
- Created [docs/demo_script.md](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/docs/demo_script.md) as the presenter speech guide for a 2.5-minute video pitch.
- Created [docs/judges_qna.md](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/docs/judges_qna.md) detailing typical competition questions and offline/privacy answers.
- Created [docs/technical_architecture.md](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/docs/technical_architecture.md) featuring layers analysis and a system Mermaid diagram.
- Updated [README.md](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/README.md) to link directly to all documentation assets under the "Final Submission Pack" section.
- Added tests in [tests/test_submission_docs_exist.py](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/tests/test_submission_docs_exist.py).

Tests and diagnostics:

- `pytest` passed 42 tests successfully (2 new submission document verification tests added).
- Verified `print_demo_checklist.py` and `check_runtime.py` output correct configurations and model files.

Known limitations:

- YOLO inference runs on CPU by default.
- Candidate suspicion scores and student identity checks are concept mock layouts.

Next recommended milestone:

- Milestone 1I: Final Repository QA and Optional Screenshot Capture.

### 2026-06-11 - Milestone 1I Final Repository QA and Optional Screenshot Capture

Performed final repository QA auditing, static page smoke tests, ignore index validation, and created the final QA report.

- Created [docs/final_qa_report.md](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/docs/final_qa_report.md) documenting pytest, checklist, runtime configs, smoke checks, and capture guides.
- Updated [PROJECT_CONTEXT.md](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/PROJECT_CONTEXT.md) to set active milestone to 1I and log all completed QA tasks.
- Added tests in [tests/test_final_qa_report_exists.py](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/tests/test_final_qa_report_exists.py).

Tests and diagnostics:

- `pytest` passed 46 tests successfully (1 new static QA document validation test added).
- Verified `print_demo_checklist.py` and `check_runtime.py` output all status criteria successfully.
- Conducted local endpoint checks verifying all web dashboards and APIs return 200.
- Confirmed with `git status --ignored` that database files, snapshots, validation reports, model weights, and logs are safely ignored.

Known limitations:

- YOLO CPU fallback active locally.
- Seating invigilation scores are concept mock signals.
- Camera and security rule thresholds require calibration with live gate recording.

Next recommended milestone:

- Manual submission package assembly and presentation practice.

### 2026-06-11 - CUDA Environment Upgrade (Environment-only, not committed)

Upgraded local PyTorch from CPU-only to CUDA 12.8 GPU acceleration.

- Uninstalled `torch 2.12.0+cpu` and installed `torch 2.11.0+cu128` from `https://download.pytorch.org/whl/cu128`.
- Pip cache kept in `.cache\pip` on F: drive (not C:).
- Verified `torch.cuda.is_available() = True`, GPU = NVIDIA GeForce RTX 3050 Laptop GPU, 4 GB VRAM.
- Validation benchmark after CUDA: ~62 FPS, ~11.69 ms average inference.
- No source files changed. No commit made. `.venv` is in `.gitignore`.

### 2026-06-11 - Milestone 1J-lite Practical Demo Reliability Improvements

Added four practical reliability improvements without destabilizing the accepted 1I state.

1. **CUDA setup documentation** — Created [docs/local_cuda_setup.md](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/docs/local_cuda_setup.md) with verified steps, rollback instructions, and rules (no commit of .venv or .cache).

2. **Gate-zone ROI filtering** — Added `GATE_ZONE_ENABLED`, `GATE_ZONE_X1/Y1/X2/Y2` config fields (normalized 0.0–1.0 frame fractions) to `core/config.py` and `.env.example`. `SecurityRulesEngine` now filters active tracks to only those whose bbox centre falls inside the configured zone. Crowding and loitering rules use gate-zone-filtered track counts. Pixel-coordinate bboxes (values > 1.5) fall back to "inside" to prevent silent track drops. Old evidence fields preserved; added `active_tracks_in_gate_zone` and `gate_zone_bbox_normalized`.

3. **Missed-frames pruning** — Added `MAX_TRACK_MISSED_FRAMES=10` config to `core/config.py`, `.env.example`. `PersonTracker._prune_old_tracks` now removes tracks when `missed_frames > max_missed_frames` OR age exceeds `max_age_seconds`. Reduces ghost tracks in demo. `get_status()` now also reports `max_missed_frames`.

4. **Raw + annotated evidence snapshots** — `VideoProcessor._save_security_event_frame` now saves both `security_event_TIMESTAMP_annotated.jpg` and `security_event_TIMESTAMP_raw.jpg`. Annotated path is the main `snapshot_path` (DB backward compatible). Raw path added to event evidence as `raw_snapshot_path` when available.

Other changes:
- Updated `api/main.py` to pass gate-zone params to `SecurityRulesEngine` and `max_missed_frames` to `PersonTracker`.
- Updated `scripts/check_runtime.py` with gate-zone config display.
- Updated `README.md` with hardware target (CUDA verified), CUDA setup link, and 1J-lite status.
- Added `tests/test_milestone_1j_lite.py` with 11 new tests.

Tests and diagnostics:

- `pytest`: **57 passed, 1 warning** (up from 46).
- `check_runtime.py`: GATE_ZONE_ENABLED displayed, MAX_TRACK_MISSED_FRAMES displayed.
- Validation: ~62 FPS, ~11.69 ms inference (GPU active).
- `git status`: clean before any commit.

Known limitations:

- Gate-zone ROI only filters normalised bboxes. Pixel-coord bboxes from the tracker bypass gate-zone filtering (safe fallback; fix would require normalising bboxes in video_processor, deferred).
- CUDA installed locally; not part of the committed project — documented in `docs/local_cuda_setup.md`.

Next recommended milestone:

- Submit for senior review. If accepted, commit and push. Then manual screenshot capture and submission package assembly.

### 2026-06-11 - Milestone 2A-UI Optional React Showcase Frontend

Added an optional Vite + React showcase frontend in `showcase-frontend/` for competition-grade presentation. The existing `dashboard/` HTML pages and FastAPI backend are completely untouched.

**Architecture:**
```
FastAPI backend (port 8002) — real AI engine, tracking, rules, DB
Vite/React      (port 5173) — optional showcase presentation layer
dashboard/                  — plain HTML fallback (always works)
```

**Files created:**
- `showcase-frontend/` — full Vite + React project
  - `vite.config.js` — dev proxy `/api` → port 8002
  - `src/index.css` — dark-mode command-center design system
  - `src/api/client.js` — safe fetch + offline fallback data
  - `src/components/NavBar.jsx`, `HumanInLoopBanner.jsx`, `SecurityLevelCard.jsx`, `TrackingPanel.jsx`, `MjpegFeed.jsx`
  - `src/pages/Landing.jsx`, `SecurityRoom.jsx`, `GuardView.jsx`, `ExamView.jsx`
  - `src/App.jsx` — hash-based router
  - `public/favicon.svg` — SmartKUET shield icon
  - `showcase-frontend/README.md`
- Updated `.gitignore` to exclude `showcase-frontend/node_modules/`, `dist/`, `.vite/`
- Updated `README.md` with optional showcase frontend section

**Build/run verification:**
- `npm install` — 135 packages, 0 vulnerabilities
- `npm run build` — success, 228ms, 0 errors
- `git status --ignored` — `node_modules/` and `dist/` confirmed ignored
- Dev server: http://localhost:5173 → 200 OK, Vite ready in 400ms
- Vite `/api` proxy verified: all proxied FastAPI endpoints return 200
- Backend pytest: 57 passed, 1 warning (unchanged)

**Git safety:**
- `showcase-frontend/node_modules/` — gitignored ✅
- `showcase-frontend/dist/` — gitignored ✅
- Old `dashboard/` HTML files — untouched ✅

Next recommended milestone:

- Screenshot capture across all four showcase pages, final PDF/summary assembly, and live presentation practice.

### 2026-06-11 - Milestone 2B Open-Source Face Verification Prototype

Added the first real face verification prototype using InsightFace + LFW open-source data.
No real KUET data used. Enrolled gallery = LFW academic identities labeled "Demo Member A/B/C".

**Architecture:**
```
CCTV frame → InsightFace (RetinaFace detect + ArcFace embed)
→ cosine similarity vs enrolled gallery embeddings
→ green (≥0.40) = Known Demo Member
→ yellow (0.30–0.40) = Low Confidence / Manual Verify
→ red (<0.30) = Unknown Visitor
→ Guard makes final gate decision
```

**Files created:**
- `docs/open_face_verification_prototype.md` — design doc, dataset roles, privacy framing
- `core/face_verification.py` — FaceVerificationService, FaceVerificationResult dataclass
- `scripts/prepare_lfw_demo_gallery.py` — LFW download + gallery image prep + enrollment
- `tests/test_milestone_2b_face.py` — 21 new tests (mock-safe, no downloads required)
- `showcase-frontend/src/components/FaceVerificationPanel.jsx` — React UI panel

**Files modified:**
- `core/config.py` — face verification config fields + ensure_project_dirs guard
- `api/main.py` — FaceVerificationService in lifespan + /api/face/* routes
- `.gitignore` — data/face_datasets/*, data/demo_face_gallery/*, data/face_embeddings/*, runs/face_verification/*
- `requirements.txt` — insightface==1.0.1, onnxruntime==1.26.0, scikit-learn
- `.env.example` — FACE_* configuration fields
- `showcase-frontend/src/pages/GuardView.jsx` — FaceVerificationPanel added
- `showcase-frontend/src/pages/Landing.jsx` — Face Verification feature card added

**New API endpoints:**
- `GET  /api/face/status` — model loaded, gallery size, threshold
- `GET  /api/face/demo-members` — enrolled member labels
- `POST /api/face/verify-image` — cosine similarity result with path traversal protection

**Test results:**
- pytest: 78 passed, 0 failed (57 prior + 21 new 2B tests)
- npm run build: ✅ 27 modules, 0 errors, 131ms
- Smoke test: all 8 endpoints → 200 OK
- InsightFace buffalo_s: loaded and serving correctly

**Known notes:**
- InsightFace model auto-downloads to user home `.insightface/` on first run (INSIGHTFACE_HOME env var must be set before module load to redirect). Model works correctly regardless of location.
- onnxruntime CPU only in test env (CUDA warning suppressed). Production GPU uses PyTorch/YOLO path.
- Gallery is empty until `python scripts/prepare_lfw_demo_gallery.py` is run (LFW ~200MB download).

**Current milestone:** Milestone 2C Local Object-Cue Detection Scaffold (branch: milestone-2c-object-cues)

Next recommended milestone:

- Milestone 2C Phase 3: Add React Object Cues panel to the optional showcase frontend.
- Milestone 2D: Risk Fusion Engine combining face status, object cues, tracking, and time rules.

### 2026-06-12 - Milestone 2C Phase 1 & 2 Local Object-Cue Detection Scaffold

Researched open-source Roboflow Universe dataset candidates and implemented a safe, offline, local-only object cue detection scaffold.

1. **Research & Curation**:
   * Evaluated candidate datasets on Roboflow Universe and documented findings in `docs/roboflow_object_cue_research.md`.
   * Curated candidates for ID-card, lanyard, name-badge, backpack/bag (pre-trained COCO), helmet (occlusion context), and uniforms/logos.
   * Defined system safety principles: object cues are supporting evidence only, known/unknown identity checks are handled by InsightFace/LFW, and human guard retains override controls.

2. **Configuration & Paths**:
   * Added `ROBOFLOW_OBJECT_CUES_ENABLED`, `ROBOFLOW_OBJECT_CUE_MODEL_PATH`, and `ROBOFLOW_OBJECT_CUE_CLASSES` configuration fields in `core/config.py` and `.env.example`.
   * Updated `ensure_project_dirs` to create `models/object_cues`, `data/roboflow_datasets`, and `runs/object_cues` locally.

3. **Repository Directory Structure**:
   * Updated `.gitignore` to unignore subdirectories while ignoring wildcards (e.g. weights `*.pt`, datasets `*`, runs `*`).
   * Created empty `.gitkeep` placeholder files under `models/object_cues/`, `data/roboflow_datasets/`, and `runs/object_cues/` to track directory structures.

4. **Service & APIs**:
   * Implemented `ObjectCueDetectionService` in `core/object_cue_detection.py` returning `DISABLED`, `MODEL_NOT_CONFIGURED`, or `READY` statuses.
   * Integrated service in app lifespan context and exposed `GET /api/object-cues/status` in `api/main.py`.

5. **Diagnostics & Tests**:
   * Updated `scripts/check_runtime.py` to print object cue diagnostics.
   * Added 5 scaffold tests in `tests/test_milestone_2c_scaffold.py`. All tests passed (83 total passed, 0 failures).
   * Completed API smoke test verifying 200 OK across `/health`, `/api/runtime/status`, `/api/security/status`, `/api/face/status`, and `/api/object-cues/status`.

6. **React UI Components (Phase 3)**:
   * Updated the showcase API client `showcase-frontend/src/api/client.js` with `fetchObjectCuesStatus` and `DEMO_OBJECT_CUES` fallback.
   * Created `ObjectCuesPanel.jsx` component displaying target cues, status badges (`DISABLED`, `MODEL_NOT_CONFIGURED`, `READY`), and the human-in-the-loop safety warning.
   * Integrated `ObjectCuesPanel` in both `GuardView.jsx` and `SecurityRoom.jsx` layouts.
   * Verified successful Vite production build (`npm run build` completed successfully, compiling 28 modules).

**Current milestone:** Milestone 2D Multi-Modal Risk Fusion Engine (branch: milestone-2d-risk-fusion)

Next recommended milestone:

- Milestone 2E: Research Evaluation & Competition Presentation Pack (benchmarks, screenshots, demo script, and stable path freeze).

### 2026-06-12 - Milestone 2D Phase 1, 2, & 3 Multi-Modal Risk Fusion Engine & React UI Panel

Successfully designed, scaffolded, integrated, and visually represented the research-grade **Multi-Modal Risk Fusion Engine** for campus gate monitoring at KUET.

1. **Design & Research (Phase 1)**:
   * Created [docs/risk_fusion_design.md](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/docs/risk_fusion_design.md) outlining the theoretical framework and campus security scenarios.
   * Specified scoring logic combining: base face similarity status, camera health availability, time-of-day (after-hours), gate-zone ROI presence, motionless person indicators, and rules engine alerts.

2. **Core Python Engine (Phase 1)**:
   * Implemented the deterministic, explainable engine in [core/risk_fusion.py](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/core/risk_fusion.py) with `RiskFusionInput` and `RiskFusionResult` schemas.
   * Added score mitigations (present lanyards/cards deduct 5 points but are floored to prevent LOW classification) and aggravators (unknown face after-hours score = 90).

3. **FastAPI Route & Integration (Phase 2)**:
   * Exposed a unified queryable GET `/api/risk-fusion/status` endpoint in [api/main.py](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/api/main.py).
   * Aggregated live states: camera status, latest security events, tracking summaries, and face verification results.
   * Supported complete testing parameter overrides (`face_status`, `camera_available`, `after_hours`, etc.) in the endpoint query string.
   * Updated `api/main.py` to preserve the outcome of the last on-demand face verification run in a global `latest_face_verification_result` tracker.

4. **Testing & QA (Phase 2)**:
   * Created unit tests in [tests/test_milestone_2d_api.py](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/tests/test_milestone_2d_api.py) validating default endpoints, mitigations, query overrides, and state updates.
   * Verified that all 95 tests pass successfully (`pytest` completed with 95 passed, 0 failures).
   * Successfully performed a live uvicorn smoke test on port `8002` verifying all endpoints return 200 and the risk fusion JSON shape matches the research-grade criteria.

5. **React UI Components (Phase 3)**:
   * Added the `fetchRiskFusionStatus` function to the show-case API client [client.js](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/showcase-frontend/src/api/client.js) with mock fallback configuration.
   * Created [RiskFusionPanel.jsx](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/showcase-frontend/src/components/RiskFusionPanel.jsx) implementing explainable advisory risk levels (LOW, MEDIUM, HIGH, CRITICAL), recommended actions, reasoning traces, and signal verification status chips (Camera, Face, Object, Tracking, Gate-Zone, Security Rules).
   * Integrated the panel into [GuardView.jsx](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/showcase-frontend/src/pages/GuardView.jsx) and [SecurityRoom.jsx](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/showcase-frontend/src/pages/SecurityRoom.jsx) layouts.
   * Verified successful Vite production build (`npm run build` completed successfully, compiling 29 modules in 143ms).

### 2026-06-12 - Milestone 2E Phase 1 Research Evaluation & Competition Presentation Pack

Successfully completed the documentation framework and evaluation protocols for competition staging and academic paper publication.

1. **System Evaluation Protocols**:
   * Created [docs/evaluation_protocol.md](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/docs/evaluation_protocol.md) outlining vitals (latency, FPS), API endpoint health metrics, correctness checks (unit tests), dataset mappings (LFW, Roboflow, local benchmarks), and ethical/advisory boundaries.

2. **Presentation Staging & Freeze**:
   * Created [docs/competition_demo_freeze.md](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/docs/competition_demo_freeze.md) establishing exact demo stories, landing page and security dashboard check grids, live backend status API routes, presenter script highlights, and claims warnings.

3. **Research Paper Skeleton**:
   * Created [docs/research_paper_skeleton.md](file:///F:/Skill_WORK/CODE/SMART_KUET_Innovative/docs/research_paper_skeleton.md) featuring full abstracts, methodology explanations, and the mathematical formulation of the risk fusion scoring algorithm.
