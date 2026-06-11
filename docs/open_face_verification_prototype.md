# Open-Source Face Verification Prototype

## Purpose

This document describes the open-source face verification prototype implemented in
Milestone 2B of SmartKUET Sentinel.

The goal is to demonstrate how a real KUET campus member database would enable
known-vs-unknown person verification at the campus gate — **without using real KUET data**.

---

## Critical Framing

> **We are NOT using real KUET student, staff, or faculty data.**
>
> The enrolled gallery consists of open-source identities from the LFW (Labeled Faces
> in the Wild) dataset, labeled anonymously as "Demo Member A", "Demo Member B", etc.
>
> In real KUET deployment, this demo gallery would be replaced by an approved KUET/hall
> member database with explicit consent and university data governance policy.

The system **cannot prove KUET membership** from open-source data. It only demonstrates
that the pipeline (detect → embed → compare → result) works correctly and could be
connected to a real approved dataset.

---

## Dataset Roles

### 1. LFW — Labeled Faces in the Wild (First Priority)

- **Role**: Main prototype dataset for known-vs-unknown demo verification.
- **Use**: Enroll 3 identities (3 images each) as "Demo Member A/B/C". Test other LFW
  identities as unknown visitors.
- **Why LFW**: Purpose-built for face verification (same/different person decision).
  Available via `sklearn.datasets.fetch_lfw_people`. Academic, open-source, CC-licensed.
- **Size**: ~200MB download, stored in `data/face_datasets/lfw/` (gitignored).
- **Reference**: Labeled Faces in the Wild, Huang et al., 2007.
  http://vis-www.cs.umass.edu/lfw/

### 2. WIDER FACE (Later — Detection Stress Testing)

- **Role**: Face detection stress-testing under CCTV-like conditions: occlusion, extreme
  pose, varying scale, crowd scenes.
- **Use**: Benchmark the InsightFace detector on hard cases before relying on it for
  campus gate verification.
- **Size**: 32,203 images, 393,703 labeled faces.
- **Priority**: After LFW prototype is stable.
- **Reference**: Yang et al., WIDER FACE: A Face Detection Benchmark, CVPR 2016.

### 3. VGGFace2 (Later — Larger Recognition Dataset)

- **Role**: Larger, more diverse face recognition dataset for training/evaluation.
- **Use**: Evaluate InsightFace embedding quality at scale across pose and age variation.
- **Size**: 3.31M images, 9,131 identities.
- **Priority**: Future — only if LFW prototype proves the pipeline.
- **Reference**: Cao et al., VGGFace2: A dataset for recognising faces across pose
  and age, FG 2018. https://arxiv.org/abs/1710.08092

### 4. CelebA (Optional — Attributes/Landmarks)

- **Role**: Face attribute dataset (40 attributes, 202,599 images, 10,177 identities).
- **Use**: Optional demo for attribute-based access (e.g., uniform/badge detection by
  combining with object detection). Not the primary identity solution.
- **Priority**: Optional/later.
- **Reference**: Liu et al., Deep Learning Face Attributes in the Wild, ICCV 2015.
  http://mmlab.ie.cuhk.edu.hk/projects/CelebA.html

### 5. Roboflow (Optional — Object Detection Only)

- **Role**: Custom object detection datasets (ID cards, badges, helmets, bags, gates).
- **Use**: Optional supplement to YOLO detection for campus-specific objects.
- **Priority**: Optional. Not used for face identity.

---

## Technical Architecture

```
CCTV Frame (BGR)
        │
        ▼
InsightFace Detector (RetinaFace)
        │  ← detects face bounding boxes
        ▼
InsightFace Recognition (buffalo_s ArcFace)
        │  ← generates 512-dim embedding per face
        ▼
Cosine Similarity Search
        │  ← compare against enrolled gallery embeddings
        ▼
┌─────────────────────────────────┐
│ similarity ≥ 0.40 → VERIFIED    │  green  · "Known Demo Member"
│ 0.30 ≤ sim < 0.40 → LOW_CONF   │  yellow · "Manual Verification"
│ similarity < 0.30 → UNKNOWN     │  red    · "Unknown Visitor"
│ no face found  → NO_FACE        │  grey   · "No face detected"
│ model missing  → UNAVAILABLE    │  grey   · "Model not loaded"
└─────────────────────────────────┘
        │
        ▼
Guard Decision Panel (Human decides gate action)
```

---

## InsightFace — Engine Details

- **Library**: `insightface==1.0.1` (MIT licensed code, non-commercial model weights)
- **Model pack**: `buffalo_s` (small, fast, ~80MB, downloads on first run to `.cache/insightface/`)
- **Detector**: RetinaFace — robust, handles pose/scale variation
- **Recogniser**: ArcFace — 512-dim embedding, cosine similarity
- **Inference**: ONNX Runtime (`onnxruntime==1.26.0`) — GPU or CPU fallback
- **Model licence**: InsightFace pretrained models are for non-commercial research use.
  This is acceptable for a university academic project prototype.

---

## Demo Gallery Structure

```
data/demo_face_gallery/          ← gitignored directory
  DemoMemberA/
    img_0.jpg  img_1.jpg  img_2.jpg
  DemoMemberB/
    img_0.jpg  img_1.jpg  img_2.jpg
  DemoMemberC/
    img_0.jpg  img_1.jpg  img_2.jpg
```

The mapping from `DemoMemberA/B/C` to real LFW identity names is printed to console by
`scripts/prepare_lfw_demo_gallery.py` but **never written to any committed file**.

---

## Privacy and Human-in-the-Loop

- **No automated gate control.** Face verification results are advisory inputs only.
- **Human guard makes all decisions**: ALLOW / VERIFY ID / DENY.
- **No permanent profiles.** Gallery is demo data only; no real person is tracked.
- **No biometric storage of KUET individuals.** Open-source demo embeddings only.
- **Unknown result = verification request, not punishment.** Guard decides next step.

---

## Real Deployment Migration Path

When this prototype is adapted for real KUET deployment:

1. Replace `data/demo_face_gallery/` with approved KUET member database images.
2. Re-run `scripts/prepare_lfw_demo_gallery.py` (or equivalent enrollment script)
   with real consented images.
3. Update display labels from "Demo Member A" to actual KUET ID / name (with consent).
4. Apply university data governance and storage policies to all face data.
5. Implement access controls on the embedding cache and gallery.

---

## Gitignored Paths

The following directories are gitignored to prevent accidental data commits:

```
data/face_datasets/       ← LFW and other downloaded datasets
data/demo_face_gallery/   ← enrolled gallery images
data/face_embeddings/     ← .npy embedding caches
runs/face_verification/   ← verification logs
.cache/insightface/       ← InsightFace model weights (auto-downloaded)
```

Only `.gitkeep` placeholder files are committed to preserve directory structure.
