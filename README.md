# SmartKUET Sentinel

SmartKUET Sentinel is an offline Edge-AI campus security and exam integrity assistant for KUET. The current build is **Milestone 1J-lite** (Practical Demo Reliability Improvements): YOLO detection with GPU acceleration, person tracking with ghost-track pruning, gate-zone ROI filtering, deterministic security rules, dual raw+annotated evidence snapshots, runtime diagnostics, validation reporting, polished dashboards, and a full submission documentation pack — all running locally with no cloud dependencies.

## Core Features

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

- Primary target: RTX 3050 4GB laptop GPU with CUDA-enabled PyTorch.
- CUDA verified working: `torch 2.11.0+cu128`, `cuda: True`, `~62 FPS` on demo video, `~11.7 ms` avg inference.
- CPU fallback: fully supported. All tests pass on CPU. Slower (~10–20 FPS).
- Do not install CUDA automatically from this project. Use the official PyTorch selector.
- See [docs/local_cuda_setup.md](docs/local_cuda_setup.md) for the verified CUDA install steps and rollback instructions.

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

## Milestone 1E Demo Validation

This milestone provides validation and tuning tools for the YOLO detection, person tracking, and security rules engine pipeline.

### Adding a Sample Video
1. Place a video file (e.g., `demo.mp4`) in the `sample_videos/` directory.
2. If `sample_videos/demo.mp4` is not present, validation scripts will print a clear instruction and exit gracefully.

### Running Validation
Run the validation script to execute the pipeline frame-by-frame and collect metrics:
```powershell
python scripts/validate_demo_video.py --source sample_videos/demo.mp4 --seconds 30
```

### Interpreting the JSON Report
Validation reports are saved in `runs/benchmarks/validation_YYYYMMDD_HHMMSS.json`. The report includes:
* `total_frames_read`: Total frames read from the video.
* `processed_frames`: Total frames where YOLO detection was run.
* `approximate_fps` & `average_inference_ms`: Performance statistics.
* `average_person_count`, `average_phone_count`, `average_vehicle_count`: Average counts of objects.
* `max_active_tracks` & `total_tracks_seen`: Tracking statistics.
* `total_security_events`, `event_count_by_type`, `event_count_by_level`, and `highest_security_level_seen`: Security rules aggregates.

### Annotated Frames
Three sample frames from different stages of the video are annotated and saved to the `runs/videos/validation_frames/` directory to visually verify detection bounding boxes, tracking labels, and rules status.

> [!IMPORTANT]
> * **No Identity Recognition**: This system does NOT perform face recognition, face identification, or verify student identities.
> * **Temporary Tracking IDs**: Track IDs (e.g., `ID 1`, `ID 2`) are short-lived numbers assigned temporarily to keep track of a target's motion across consecutive frames, and do not represent student identities.
> * **Human Decision-making**: The automated security alerts provide cues and instruction recommendations. The final gate control action (e.g., Allow, Deny, Verify ID) is determined entirely by the human security guard.

## Demo Video Attribution and Privacy

To protect the privacy of campus members and ensure professional standards:
* **Private Faces**: Do not upload or record footage showing private faces without explicit consent, especially if dashboard screenshots or visual reports will be published.
* **Public Sample Video Attribution**: If you are using open-source validation assets (such as the Intel IoT DevKit sample videos), make sure to reference [sample_videos/ATTRIBUTION.md](sample_videos/ATTRIBUTION.md).
* **Consented Local Footage**: For the final project submission or live presentation, we strongly recommend recording your own local gate footage with consented participants.
* **Temporary Track IDs**: Remember that track IDs (like `ID 1`, `ID 2`) are temporary indicators to trace motion across adjacent frames and do not represent student identity or permanent profiles.

## Final Submission Pack

The following documents compile the pitch, design, runbooks, and checklists for the KUET innovation submission:
* **Final Submission Pack**: [docs/final_submission_pack.md](docs/final_submission_pack.md) — Implemented features, validation results, and checklists.
* **Spoken Demo Script**: [docs/demo_script.md](docs/demo_script.md) — Presenter script for a 2.5-minute pitch video.
* **Judges Q&A Prep**: [docs/judges_qna.md](docs/judges_qna.md) — Anticipated questions and strong responses.
* **Technical Architecture**: [docs/technical_architecture.md](docs/technical_architecture.md) — System flow diagram and architectural layers.
* **Demo Runbook**: [docs/demo_runbook.md](docs/demo_runbook.md) — Developer checklists, run commands, and screenshot guides.
* **Submission Pitch**: [docs/submission_pitch.md](docs/submission_pitch.md) — Innovation concept proposal detail.
* **Final QA Report**: [docs/final_qa_report.md](docs/final_qa_report.md) — Repository QA audit and presentation checklist.
* **Local CUDA Setup**: [docs/local_cuda_setup.md](docs/local_cuda_setup.md) — Optional GPU acceleration guide with verified steps and CPU rollback.
* **Video Attributions**: [sample_videos/ATTRIBUTION.md](sample_videos/ATTRIBUTION.md) — Dataset licenses and privacy standards.

## Current Status

Milestone 1J-lite (Practical Demo Reliability Improvements) is complete. GPU acceleration verified at ~62 FPS. Gate-zone ROI filtering, missed-frames pruning, and dual evidence snapshots added. Next step: manual screenshot capture, proposal PDF assembly, and live presentation practice.
