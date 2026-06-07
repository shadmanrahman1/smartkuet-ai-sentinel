# SmartKUET Sentinel Project Context

This file is the running Codex work log for this project. Each time Codex works on the project, update this file with what changed, why it changed, and the current project context needed for the next session.

## Current Context

- Project folder: `F:\Skill_WORK\CODE\SMART_KUET_Innovative`
- Project name: SmartKUET Sentinel
- Current milestone: Milestone 1D security event rules engine
- Runtime target: local/offline deployment from the project drive
- Important constraint: keep project runtime files, cache, virtual environment, database, snapshots, and sample videos inside this project folder/local drive. Avoid using `C:` for project configuration or runtime artifacts.
- Frontend stack: plain HTML, local CSS, and vanilla JavaScript. No React or Next.js.
- Backend stack: FastAPI, Uvicorn, OpenCV, SQLite, WebSockets, Ultralytics YOLO, Torch.
- YOLO is now included for object/person detection with runtime diagnostics, evidence capture, person tracking, and deterministic security event rules. No face recognition, InsightFace, MediaPipe, exam behavior scoring, training, or cloud APIs yet.

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
- Next recommended milestone: Milestone 1E, validate with a real local CCTV/sample video and tune thresholds before identity features.
