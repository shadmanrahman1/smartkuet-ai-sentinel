# SmartKUET Sentinel - Demo & Recording Runbook

This runbook guides reviewers and developers through the steps to verify, execute, and capture screenshots of SmartKUET Sentinel.

## Demo Setup Checklist

1. **Python Environment**: Ensure you have Python 3.10+ (tested on Python 3.13) and the virtual environment is activated:
   ```powershell
   .\.venv\Scripts\activate
   ```
2. **YOLO Model**: Verify that `models/yolov8n.pt` has been downloaded locally in the `models/` directory.
3. **Demo Video Source**: Place a local CCTV or gate recording at `sample_videos/demo.mp4`.
   > [!WARNING]
   > **Do NOT commit or add `demo.mp4` to Git.** Large video files are excluded from commits by the configured `.gitignore`.

## Recommended Commands

Run these commands in order to execute the validation pipeline and host the sentinel service:

### 1. Print Demo Checklist
Run the checklist script to verify local dependencies, model paths, and validation output directory states:
```powershell
python scripts/print_demo_checklist.py
```

### 2. Run Video Pipeline Validation
Execute the detector, tracking, and rules engine on the demo video for 30 seconds to generate metrics and validation sample frames:
```powershell
python scripts/validate_demo_video.py --source sample_videos/demo.mp4 --seconds 30 --write-summary
```
* **JSON Metrics**: Output is written to `runs/benchmarks/validation_YYYYMMDD_HHMMSS.json`.
* **Markdown Summary**: Proposal summary is compiled into `runs/benchmarks/latest_validation_summary.md`.
* **Annotated Frame Samples**: 3 verification frames are saved as JPEGs inside `runs/videos/validation_frames/`.

### 3. Start local Uvicorn Server
Host the Sentinel web service locally on port `8002` (port `8000` is avoided due to environment conflicts):
```powershell
uvicorn api.main:app --reload --port 8002
```

## Pages to Open & Screenshot Guide

Once the server is running, open the following URLs in your browser to view the interface:

1. **Central Dashboard**: [http://127.0.0.1:8002/](http://127.0.0.1:8002/)
   * **Focus**: Capture the top banner, the live stream canvas with YOLO bounding boxes + track labels, detection panels, and current active security rule alerts (Green/Yellow/Orange/Red).
2. **Guard Interface**: [http://127.0.0.1:8002/guard](http://127.0.0.1:8002/guard)
   * **Focus**: Capture the mobile-first layouts showing the enlarged alert indicator block, gate instruction, action buttons (ALLOW, VERIFY ID, DENY), and the human-in-the-loop disclaimer.
3. **Examiner Interface**: [http://127.0.0.1:8002/exam](http://127.0.0.1:8002/exam)
   * **Focus**: Capture the invigilator dashboard with the candidate seat status cards, suspicion score tracking, suspicion level references, and invigilator overrides.
4. **Validation Summary**: Open the generated `runs/benchmarks/latest_validation_summary.md` and capture the rendered proposal table/report metrics.

## Privacy & Attribution Guidelines

* **Privacy Standard**: For final presentation materials, record custom local footage at a KUET gate using consented participants. Avoid filming or presenting private faces without explicit permission.
* **Open-Source Attribution**: If you utilize publicly available video benchmarks (e.g. from the Intel IoT DevKit datasets), confirm the licensing and write attributes inside `sample_videos/ATTRIBUTION.md`.
