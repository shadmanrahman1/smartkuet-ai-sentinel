# SmartKUET Sentinel - Final Repository QA Report

This report documents the final quality assurance validation of the SmartKUET Sentinel repository.

---

## QA Metadata
*   **Evaluation Date/Time**: 2026-06-11 (16:05 Local Time)
*   **Active Milestone**: Milestone 1I Final Repository QA and Optional Screenshot Capture
*   **Latest Commit Hash**: `b4f5c4ea77eaef25dac580698b1ca96e000beca4`
*   **Repository URL**: [https://github.com/shadmanrahman1/smartkuet-ai-sentinel](https://github.com/shadmanrahman1/smartkuet-ai-sentinel)

---

## QA Checks Summary

### 1. Test Suite Results
*   **Command**: `.venv\Scripts\python -m pytest`
*   **Status**: Passed
*   **Metrics**: 45 passed, 1 warning.
*   **Coverage**: Verified all database helpers, cameras, config paths, tracking boundaries, and static page checks.

### 2. Checklist & Dependency States
*   **Command**: `.venv\Scripts\python scripts/print_demo_checklist.py`
*   **Status**: Passed
*   **Checklist Output**:
    1.  `sample_videos/demo.mp4` exists: **True** (locally available)
    2.  `sample_videos/ATTRIBUTION.md` exists: **True**
    3.  `models/yolov8n.pt` exists: **True** (locally cached)
    4.  Runs benchmarks directory exists: **True**
    5.  Validation frames directory exists: **True**
    6.  PyTorch CUDA status: **Unavailable (CPU fallback active)**

### 3. Runtime Environment Check
*   **Command**: `.venv\Scripts\python scripts/check_runtime.py`
*   **Status**: Passed
*   **Output Summary**: Verified clean virtual environment paths on `F:\` drive. confirmed Torch and Ultralytics wrappers map to project folders.

### 4. Git Ignore Safety Verification
*   **Command**: `git status --ignored`
*   **Status**: Confirmed safe
*   **Excluded Files**:
    *   `sample_videos/demo.mp4`
    *   `runs/benchmarks/*.json`
    *   `runs/benchmarks/latest_validation_summary.md`
    *   `runs/videos/validation_frames/*.jpg`
    *   `snapshots/evidence/*.jpg`
    *   `models/yolov8n.pt`
    *   `smartkuet.db`
    *   `.venv/` & `.cache/`
    All generated outputs and model parameters are strictly ignored and remain excluded from the Git index.

### 5. Local Endpoint Smoke Test
*   **Command**: `.venv\Scripts\python -m uvicorn api.main:app --host 127.0.0.1 --port 8002`
*   **Status**: Passed
*   **Checked URLs**:
    *   `http://127.0.0.1:8002/` -> **200 OK**
    *   `http://127.0.0.1:8002/guard` -> **200 OK**
    *   `http://127.0.0.1:8002/exam` -> **200 OK**
    *   `http://127.0.0.1:8002/dashboard/app.js` -> **200 OK**
    *   `http://127.0.0.1:8002/dashboard/styles.css` -> **200 OK**
    *   `http://127.0.0.1:8002/health` -> **200 OK**
    *   `http://127.0.0.1:8002/api/runtime/status` -> **200 OK**
    *   `http://127.0.0.1:8002/api/security/status` -> **200 OK**
*   **Cleanup**: Server stopped, and background ports `8001` and `8002` are clean.

---

## Presentation & Screenshot Checklist

When launching the demo locally, the evaluator/presenter should manually record the following screenshot targets:
1.  **Central Admin Monitor**: Navigate to `http://127.0.0.1:8002/`. Capture the dark-theme admin monitoring page including the active person tracking lists, hardware telemetry meters, and live video stream.
2.  **Guard Station Console**: Navigate to `http://127.0.0.1:8002/guard`. Capture the mobile-responsive gate display showing status alert tiles and manual gate controls.
3.  **Invigilator Integrity Page**: Navigate to `http://127.0.0.1:8002/exam`. Capture the candidate suspicion scoring board and suspicion level lookup reference.
4.  **Tuned summary metrics**: Render and capture `runs/benchmarks/latest_validation_summary.md` on the browser or markdown viewer.

---

## Ethical & Privacy Disclosures
*   **Human-in-the-Loop Assist**: AI behaves as a decision-support cue only, providing alerts and instruction recommendations. The final control actions (e.g. entry approval or invigilation warnings) remain strictly with the human guards or examiners.
*   **No Student Face Recognition**: Tracking operates entirely on temporary IDs to track motion coordinates. The system does not identify students, verify candidate names, or save facial signatures.
*   **Data Sovereignty**: The Sentinel runs entirely offline. No cloud connections, external trackers, or remote APIs are utilized, keeping campus footage completely private on local machines.

---

## Technical Limitations
*   **CPU Inference**: Inference is configured for CPU fallback by default, running at ~35-50 FPS. Dedicated deployments on Nvidia GPUs will operate faster.
*   **Mock Hall Cues**: Suspicion scores are generated mock coordinates for demo purposes. Gesture recognition models represent future work.

---

## Final Submission Recommendation
The repository has been successfully audited, tested, and cleared of all temporary benchmark outputs. We recommend staging only source code, markdown pitches, runbooks, and tests, then proceeding to manual proposal screenshot assembly.
