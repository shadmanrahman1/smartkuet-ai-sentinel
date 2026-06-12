# SmartKUET Sentinel: Presentation Screenshot Checklist (Milestone 2E)

This document provides a checklist of all screenshots required for competition slides, project submissions, and research paper figures. 

> [!WARNING]
> **Do not commit raw screenshot image files (PNG, JPG, etc.) to the repository.** Save them locally on your machine for compilation into the slide deck.

---

## 1. File Naming Conventions
To keep presentation resources organized, use the following lowercase snake_case naming scheme when saving screenshots locally:
* `showcase_landing_page.png`
* `dashboard_security_room.png`
* `dashboard_guard_view.png`
* `dashboard_exam_view.png`
* `api_health_status.png`
* `api_runtime_status.png`
* `api_face_status.png`
* `api_object_cues_status.png`
* `api_risk_fusion_normal.png`
* `api_risk_fusion_critical.png`
* `validation_snapshot_document.png`

---

## 2. Screenshot Checklist

### A. Frontend React UI Dashboards
- [ ] **React Landing Page (`/`)**: Show the clean, modern entry interface of the showcase app.
- [ ] **React Security Room Dashboard (`/security`)**: Capture the full view showing YOLO motion tracks, active event stream logs, and the **Explainable Multi-Modal Risk Fusion Panel**.
- [ ] **React Guard View Page (`/guard`)**: Highlight the face verification frame side-by-side with the **Object Cues Panel** and the **Risk Fusion Engine Details**.
- [ ] **React Exam View Page (`/exam`)**: Show the mock exam center compliance panel and rules status.

### B. Backend FastAPI Responses
- [ ] **FastAPI `/health`**: Simple JSON validation output.
- [ ] **FastAPI `/api/runtime/status`**: Showing active project directories, YOLO models, and PyTorch CUDA GPU verification.
- [ ] **FastAPI `/api/face/status`**: Showing loaded gallery size (3 members) and threshold configuration.
- [ ] **FastAPI `/api/object-cues/status`**: Confirming the `DISABLED` scaffold state and supported cue classes.
- [ ] **FastAPI `/api/risk-fusion/status` (Default)**: Normal Medium risk state.
- [ ] **FastAPI `/api/risk-fusion/status` with parameters**:
  - [ ] `?face_status=KNOWN&camera_available=true&after_hours=false` (Low Risk scenario).
  - [ ] `?face_status=UNKNOWN&after_hours=true` (Critical Risk scenario).

### C. Documentation & Diagnostics
- [ ] **Validation Snapshot Doc (`docs/validation_snapshot_2e.md`)**: The Markdown representation in your editor showing the local benchmark results.
- [ ] **README Feature Summary**: The updated current-state section of `README.md`.

---

## 3. Capture Walkthrough for Presentation Slides

1. **Slide 3 (System Architecture)**: Embed a collage of `/api/runtime/status` JSON and the `showcase_landing_page.png`.
2. **Slide 5 (Explainable Risk Fusion)**: Embed `dashboard_security_room.png` with a zoom-in on the **Explainable Multi-Modal Risk Fusion Panel** to show how signals combine deterministically.
3. **Slide 6 (Local Performance & Privacy)**: Combine `api_risk_fusion_critical.png` showing the privacy disclaimer footer with a screenshot of the benchmark table from `validation_snapshot_2e.md`.
