# SmartKUET Sentinel

SmartKUET Sentinel is an offline Edge-AI campus security and exam integrity assistant for KUET. The current build is Milestone 1D: security event rules on top of YOLO detection, person tracking, stable video input, diagnostics, benchmarking, and evidence capture.

## Milestone 1D Scope

- FastAPI app with dashboard, health, database, MJPEG, WebSocket, detection, tracking, security rules, camera, video, runtime, and evidence routes.
- Robust OpenCV camera input for webcam index, local video files, phone/IP camera URLs, and RTSP/CCTV URLs.
- Lazy Ultralytics YOLO detector using `models/yolov8n.pt` by default.
- Person-only tracking with temporary track IDs.
- IoU fallback tracker backend exposed as `iou_fallback`.
- Tracking summary at `/api/tracking/latest`.
- Tracker reset at `POST /api/tracking/reset`.
- Security rules status at `/api/security/status`.
- Security rule cooldown reset at `POST /api/security/rules/reset`.
- Rule-generated yellow, orange, and red incidents saved to the existing SQLite `security_incidents` table.
- Optional security event snapshots saved to `snapshots/evidence/`.
- Runtime diagnostics for Python, OpenCV, Torch, CUDA, Ultralytics, camera state, inference time, effective FPS, and tracking state.
- Evidence snapshot capture to `snapshots/evidence/`.
- YOLO benchmark script with tracking and security-rule metrics written to `runs/benchmarks/`.

## Detection vs Tracking

Detection answers: what objects are visible in this frame?

Tracking answers: which detected person appears to be the same temporary subject across nearby frames?

Tracking does **not** identify a person. It only assigns short-lived track IDs such as `ID 3` while a person remains visible. Face recognition is intentionally not implemented yet.

## Security Rules

The rules engine is deterministic and uses current tracking, detection, camera, and time signals:

- `NORMAL_ACTIVITY`: active persons with no concerning cue.
- `CROWDING`: active person tracks reach `CROWDING_PERSON_THRESHOLD`.
- `LOITERING`: a track age reaches `LOITER_SECONDS`.
- `PHONE_VISIBLE_AT_GATE`: YOLO reports a phone.
- `VEHICLE_NEAR_ENTRY`: YOLO reports a vehicle.
- `CAMERA_UNAVAILABLE`: camera is not opened or has no frames.
- `AFTER_HOURS_ACTIVITY`: people are visible outside configured normal hours.
- `HIGH_RISK_COMBINED`: after-hours crowding, after-hours loitering, or camera issue.

Yellow, orange, and red rule events can create DB incidents and evidence snapshots. Green normal events are displayed but not stored as incidents.

## Intentionally Not Implemented Yet

- Face recognition or face embeddings.
- InsightFace.
- MediaPipe.
- Real exam behavior scoring.
- Model training.
- Cloud services or external runtime APIs.

## Hardware Target

- Primary target: RTX 3050 4GB laptop GPU after manual CUDA-enabled PyTorch install.
- Current fallback: CPU-only inference is supported, but slower.
- Do not install CUDA automatically from this project. Use the official PyTorch selector and choose the command matching the local NVIDIA driver, Python, pip, and CUDA runtime.

## Local Drive Setup

Run these commands from this project folder:

```powershell
.\scripts\local_env.ps1
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --cache-dir .\.cache\pip -r requirements.txt
```

Copy `.env.example` to `.env` only if you need to change defaults.

Common security rule settings:

```txt
SECURITY_RULES_ENABLED=true
SECURITY_NORMAL_START_HOUR=6
SECURITY_NORMAL_END_HOUR=22
CROWDING_PERSON_THRESHOLD=4
LOITER_SECONDS=15
SECURITY_EVENT_COOLDOWN_SECONDS=10
SECURITY_HIGH_RISK_COOLDOWN_SECONDS=5
SECURITY_LOCATION=KUET Main Gate
SECURITY_SAVE_EVENT_SNAPSHOT=true
```

## Video Sources

Webcam:

```txt
CAMERA_SOURCE=0
```

Local video:

```txt
CAMERA_SOURCE=sample_videos/demo.mp4
CAMERA_LOOP_VIDEO=true
```

Phone/IP camera:

```txt
CAMERA_SOURCE=http://PHONE_IP:8080/video
```

RTSP/CCTV:

```txt
CAMERA_SOURCE=rtsp://example.com/stream
```

Put demo videos in `sample_videos/`. The project does not download external datasets or videos automatically.

## Run

Port `8000` is used by another local project in this environment, so use `8002` for SmartKUET:

```powershell
uvicorn api.main:app --reload --port 8002
```

Open:

- http://127.0.0.1:8002
- http://127.0.0.1:8002/guard
- http://127.0.0.1:8002/exam
- http://127.0.0.1:8002/api/runtime/status
- http://127.0.0.1:8002/api/tracking/latest
- http://127.0.0.1:8002/api/security/status

## Tracking Controls

Reset temporary person tracks:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8002/api/tracking/reset
```

The central dashboard also has a `Reset Tracker` button.

## Security Rule Controls

Reset rule cooldowns:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8002/api/security/rules/reset
```

The central dashboard also has a `Reset Security Rule Cooldowns` button.

## Evidence Snapshot

From the dashboard, click `Save Evidence Snapshot`.

API:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8002/api/evidence/snapshot
```

Snapshots are saved to `snapshots/evidence/` when a live frame is available.

## Runtime Check

```powershell
python scripts/check_runtime.py
```

This reports Python, OpenCV, Torch, CUDA, Ultralytics, YOLO model, tracking config, security rule config, and local runtime directory status.

## YOLO Benchmark

```powershell
python scripts/benchmark_yolo.py --source sample_videos/demo.mp4 --seconds 20
python scripts/benchmark_yolo.py --source 0 --seconds 20
```

Reports are saved to `runs/benchmarks/` and include average active tracks, max active tracks, total tracks seen, event counts by type, event counts by level, total security events, and highest level seen. CPU-only Torch works, but expect lower FPS than a CUDA-enabled Torch build.

## Test

```powershell
pytest
```

The tests do not load the YOLO model and do not require camera hardware.

## Troubleshooting

Camera unavailable:

- Check `CAMERA_SOURCE`.
- Use `sample_videos/demo.mp4` or a phone IP camera URL if the webcam fails.
- The app serves a generated fallback frame when no camera frame is available.

CUDA unavailable:

- `scripts/check_runtime.py` will show CUDA status.
- CPU-only Torch is supported.
- For RTX 3050 acceleration, install CUDA-enabled PyTorch manually using the official PyTorch selector.

Tracking unavailable:

- Confirm `TRACKING_ENABLED=true`.
- The current backend is `iou_fallback`, which is simple and CPU-friendly.
- Temporary IDs can change when people leave the frame, overlap heavily, or the camera feed drops.

Security rules not firing:

- Confirm `SECURITY_RULES_ENABLED=true`.
- Check `/api/security/status` for current level, instruction, cooldowns, thresholds, and evidence values.
- Use `POST /api/security/rules/reset` if a repeated condition is intentionally under cooldown.

Next recommended milestone: Milestone 1E, validate the rules with a real local CCTV/sample video and tune thresholds before adding identity features. Face recognition should still wait.
