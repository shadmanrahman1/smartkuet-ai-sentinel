# Roboflow Object-Cue Detection Research

This document outlines the research and candidate datasets evaluated for **Milestone 2C: Roboflow Object-Cue Detection Prototype** in the SmartKUET Sentinel project.

---

## 1. System Framing & Core Principles

Before deploying auxiliary object-detection features, the system adheres to these core design and security principles:

* **Supporting Evidence Only**: Roboflow-derived or localized object cues (such as ID cards, lanyards, or uniforms) serve as **supporting signals** to calculate a cumulative entry risk score. They do not function as standalone authenticators.
* **No Proof of KUET Membership**: Detecting a lanyard, bag, or a card does **not** prove university membership. Cues only establish contextual compliance (e.g., "carrying student bag," "wearing lanyard").
* **Primary Identity Layer**: The **InsightFace + LFW face verification engine** remains the sole biometric identity verification layer. If face verification fails or is unknown, entry is flagged as unsafe regardless of object cues.
* **Human-in-the-Loop Override**: All decisions remain advisory. The system reports risk probabilities to the security console, and the **human security guard** retains final gate-control authority to allow, inspect, or deny entry.

---

## 2. Research Categories & Candidate Datasets

The following table summarizes candidate datasets analyzed for campus gate security cues:

### Candidate Dataset Overview

| Category | Dataset Name / Identifier | Primary Classes | Image Count (Approx.) | License / Usage Caution | YOLO Export | Verification Status / Candidate Strength |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ID-Card** | [ID cards dataset](https://universe.roboflow.com/id-recognition-workspace/id-cards-dataset) | `id-card` | ~161 | Open Access (CC BY 4.0) | High | **Verified from visible page** / Useful but small |
| **Lanyard** | [Lanyard Detection Dataset](https://universe.roboflow.com/ajr-pajsf/lanyard-detection-w0kns) | `CCS_Lanyard`, `PSUB_Lanyard` | ~60 | Open Access | High | **Verified from visible page** / Useful but small |
| **Visitor Badge** | [Name badge detection](https://universe.roboflow.com/roboflow-4j5rb/name-badge-detection) | `name-badge` | ~101 | CC BY 4.0 | High | **Verified from visible page** / Strong candidate |
| **Bag/Backpack** | [Standard COCO / Search: backpack](https://universe.roboflow.com/search?q=backpack) | `backpack`, `handbag` | ~3,000+ (COCO) | Academic / Open Source | High | **Verified (COCO pre-trained)** / Strong candidate |
| **Helmet** | [Safety Helmet Wearing Dataset (SHWD)](https://universe.roboflow.com/search?q=helmet) | `helmet`, `no-helmet` | ~7,581 | MIT License | High | **Verified from repository** / Strong candidate |
| **Uniform/Logo** | [School Logo Detection](https://universe.roboflow.com/final-project-abpfp/school-logo-detection-u24qe) | `BC`, `GT`, `Ohio State` (Logos) | ~500 | Educational | High | **Needs manual page review** / Weak candidate (experimental) |

---

## 3. Candidate Dataset Profiles

Detailed breakdown of each candidate for localized deployment:

### 1. ID-Card Detection
* **Dataset Identifier**: `id-recognition-workspace/id-cards-dataset`
* **URL**: [https://universe.roboflow.com/id-recognition-workspace/id-cards-dataset](https://universe.roboflow.com/id-recognition-workspace/id-cards-dataset)
* **Classes**: `id-card`
* **Approximate Image Count**: ~161 open-source ID-card images
* **License/Usage Caution**: CC BY 4.0. Contains images of sample/mock ID cards. Care must be taken to ensure no real personal identifying information (PII) is included.
* **YOLO Export Suitability**: High. Already annotated with bounding boxes, ready for export in YOLOv8 PyTorch format.
* **Local/Offline Usefulness**: High. Used locally on the gate edge server to trigger a "Verify ID Card" status overlay when a card is held up to the camera.
* **Verification Status / Strength**: **Verified from visible page / Useful but small**. The low image count limits absolute generalization, but it is highly suitable for initial prototyping of card detection triggers.

### 2. Lanyard Detection
* **Dataset Identifier**: `ajr-pajsf/lanyard-detection-w0kns`
* **URL**: [https://universe.roboflow.com/ajr-pajsf/lanyard-detection-w0kns](https://universe.roboflow.com/ajr-pajsf/lanyard-detection-w0kns)
* **Classes**: `CCS_Lanyard`, `PSUB_Lanyard`
* **Approximate Image Count**: ~60 open-source lanyard images
* **License/Usage Caution**: Open Access (CC BY 4.0). Some images are taken in specific office environments; model training may require domain adaptation for campus gate backgrounds.
* **YOLO Export Suitability**: High. Annotation files map directly to standard YOLO class indexing.
* **Local/Offline Usefulness**: High. Used to determine if a student is displaying a lanyard, which helps verify access credentials without interrupting student flow.
* **Verification Status / Strength**: **Verified from visible page / Useful but small**. With only 60 images, this dataset serves as a minor cue verification tool rather than a robust standalone detector.

### 3. Visitor Badge Detection
* **Dataset Identifier**: `roboflow-4j5rb/name-badge-detection`
* **URL**: [https://universe.roboflow.com/roboflow-4j5rb/name-badge-detection](https://universe.roboflow.com/roboflow-4j5rb/name-badge-detection)
* **Classes**: `name-badge`
* **Approximate Image Count**: ~101 open-source images
* **License/Usage Caution**: CC BY 4.0. Designed for close-range desk name badges; needs to be evaluated for long-range gate CCTV camera visibility.
* **YOLO Export Suitability**: High. Official Roboflow curation ensures standard format validation.
* **Local/Offline Usefulness**: High. Allows the system to classify non-members carrying visitor badges, preventing false "unknown intrusion" alerts.
* **Verification Status / Strength**: **Verified from visible page / Strong candidate**. Provides clean, standardized bounding boxes of name badges for visitor identification.

### 4. Bag/Backpack Detection
* **Dataset Identifier**: `Standard COCO / Search: backpack`
* **URL**: [https://universe.roboflow.com/search?q=backpack](https://universe.roboflow.com/search?q=backpack)
* **Classes**: `backpack`, `handbag`, `bag`
* **Approximate Image Count**: 3,000+ images (standard COCO split)
* **License/Usage Caution**: Varies by specific Universe project, but standard COCO dataset weights for YOLOv8 already include pre-trained `backpack` and `handbag` classes.
* **YOLO Export Suitability**: Extremely High. Pre-trained COCO weights (`yolov8n.pt`) already contain these classes. We do not need a custom dataset export for basic bag detection.
* **Local/Offline Usefulness**: High. Zero-setup required for basic bag detection using the active YOLO detector. Can run fully offline out-of-the-box.
* **Verification Status / Strength**: **Verified (COCO pre-trained) / Strong candidate**. Directly available using the project's existing pre-trained model weights.

### 5. Helmet Detection
* **Dataset Identifier**: `Safety Helmet Wearing Dataset (SHWD)`
* **URL**: [https://universe.roboflow.com/search?q=helmet](https://universe.roboflow.com/search?q=helmet) / GitHub / Kaggle standard repositories
* **Classes**: `helmet`, `no-helmet`
* **Approximate Image Count**: ~7,581 images
* **License/Usage Caution**: MIT License. Useful for helmet and face-occlusion context, **not identity**.
* **YOLO Export Suitability**: Extremely High. SHWD is a classic object detection benchmark dataset.
* **Local/Offline Usefulness**: High. Identifies motorcycle riders or security-compliant visitors wearing helmets. Also warns the guard if a person has their face hidden/occluded by a helmet, which prevents biometric face verification.
* **Verification Status / Strength**: **Verified from repository / Strong candidate**. Excellent dataset volume and licensing for reliable offline helmet detection.

### 6. Uniform/Logo Detection (Emblem Classification)
* **Dataset Identifier**: `final-project-abpfp/school-logo-detection-u24qe`
* **URL**: [https://universe.roboflow.com/final-project-abpfp/school-logo-detection-u24qe](https://universe.roboflow.com/final-project-abpfp/school-logo-detection-u24qe)
* **Classes**: University logos (`BC`, `GT`, `Ohio State`)
* **Approximate Image Count**: ~500 images
* **License/Usage Caution**: Educational/Non-commercial use.
* **YOLO Export Suitability**: High. Suitable for customized YOLOv8 logo detection.
* **Local/Offline Usefulness**: High. Serves as a prototype concept for training a localized YOLOv8 classifier to detect the **KUET crest** on uniforms, providing strong campus correlation.
* **Verification Status / Strength**: **Needs manual page review / Weak candidate**. Marked as experimental since logo detection datasets tend to be highly domain-specific and school crest labels require manual verification for campus validation.

---

## 4. Final Recommendations & Implementation Roadmap

Based on the dataset volume, verification status, and technical complexity:

1. **Best Immediate Object Cues for SmartKUET**:
   * **ID-Card, Lanyard, and Name Badge** are the strongest candidates to prioritize. Even with small dataset counts (~60 for lanyard, ~161 for ID-card), they cover the core requirements of verifying standard entry accessories and credentials.
2. **Best Already-Available Non-Custom Cue**:
   * **COCO backpack/handbag** detection via the existing pre-trained `yolov8n.pt` model weights. This is already functional offline with zero setup.
3. **Best Paper-Grade Secondary Cue**:
   * **Helmet / Occlusion detection** using the Safety Helmet Wearing Dataset (SHWD). Detecting helmets offers a strong contextual signal to flag biometric face occlusion (face verification score suppression) for paper evaluation.
4. **Uniform / Logo detection**:
   * Should be kept as **experimental** unless a strong, campus-verified KUET uniform dataset is collected and validated.
