"""
scripts/prepare_lfw_demo_gallery.py — Milestone 2B

Prepares a local demo face gallery from the LFW (Labeled Faces in the Wild)
open-source dataset for use with the SmartKUET face verification prototype.

Privacy notice:
  - Uses only open-source LFW academic data (not real KUET data).
  - Identity mapping (DemoMemberA → real LFW name) is printed to console only.
  - Gallery images are stored in data/demo_face_gallery/ (gitignored).
  - Do NOT commit gallery images to git.

Usage:
  .venv\\Scripts\\python scripts\\prepare_lfw_demo_gallery.py

First run downloads ~200MB of LFW data to data/face_datasets/lfw/.
Subsequent runs use the cached download.
"""

import os
import sys
from pathlib import Path

# ── Ensure project root on path ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault("ULTRALYTICS_CONFIG_DIR", str(PROJECT_ROOT / ".cache" / "ultralytics"))

from core.config import settings  # noqa: E402

import shutil
import numpy as np


GALLERY_DIR    = settings.face_gallery_dir
DATASET_DIR    = settings.data_dir / "face_datasets" / "lfw"
NUM_MEMBERS    = 3       # number of demo identities to enroll
IMAGES_EACH    = 3       # images per demo member (used for enrollment)
MIN_FACES      = 8       # minimum LFW images required per identity
MEMBER_LABELS  = ["DemoMemberA", "DemoMemberB", "DemoMemberC",
                   "DemoMemberD", "DemoMemberE"]


def fetch_lfw(data_home: Path):
    print(f"Fetching LFW dataset (min_faces_per_person={MIN_FACES}) ...")
    print(f"  Download/cache dir: {data_home}")
    print("  This may take a few minutes on first run (~200MB).\n")

    from sklearn.datasets import fetch_lfw_people

    lfw = fetch_lfw_people(
        data_home=str(data_home),
        min_faces_per_person=MIN_FACES,
        resize=0.5,
        color=True,
    )
    return lfw


def save_gallery(lfw, gallery_dir: Path) -> dict[str, str]:
    """
    Select NUM_MEMBERS identities, save IMAGES_EACH images each to gallery.
    Returns mapping {DemoMemberX: real_lfw_name} (for console display only).
    """
    import cv2
    from PIL import Image

    target_names = lfw.target_names  # array of identity name strings
    targets      = lfw.target        # array of identity indices per image
    images       = lfw.images        # (N, H, W, 3) float32 [0,1]

    # Pick identities that have enough images
    from collections import defaultdict
    identity_images: dict[int, list[int]] = defaultdict(list)
    for idx, t in enumerate(targets):
        identity_images[int(t)].append(idx)

    # Sort by most images (most data = better gallery)
    sorted_ids = sorted(identity_images.keys(),
                        key=lambda k: len(identity_images[k]),
                        reverse=True)

    selected = sorted_ids[:NUM_MEMBERS]
    mapping: dict[str, str] = {}

    if gallery_dir.exists():
        shutil.rmtree(gallery_dir)
    gallery_dir.mkdir(parents=True, exist_ok=True)

    for member_idx, identity_id in enumerate(selected):
        label = MEMBER_LABELS[member_idx]
        real_name = str(target_names[identity_id]).replace("_", " ")
        mapping[label] = real_name

        member_dir = gallery_dir / label
        member_dir.mkdir(parents=True, exist_ok=True)

        img_indices = identity_images[identity_id][:IMAGES_EACH]
        for i, img_idx in enumerate(img_indices):
            img_float = images[img_idx]  # (H, W, 3), float32 [0,1]
            img_uint8 = (img_float * 255).astype("uint8")
            # Convert RGB → BGR for OpenCV save
            img_bgr = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2BGR)
            out_path = member_dir / f"img_{i}.jpg"
            cv2.imwrite(str(out_path), img_bgr)

        print(f"  {label}: {len(img_indices)} images saved  "
              f"(mapped to LFW identity — see console only)")

    return mapping


def enroll_embeddings(gallery_dir: Path) -> None:
    """Re-enroll gallery embeddings using FaceVerificationService."""
    from core.face_verification import FaceVerificationService

    svc = FaceVerificationService(
        gallery_dir=gallery_dir,
        embeddings_cache_path=settings.face_embeddings_cache,
        insightface_cache_dir=settings.face_insightface_cache_dir,
        model_name=settings.face_model_name,
        threshold=settings.face_verification_threshold,
        low_confidence_threshold=settings.face_low_confidence_threshold,
    )

    if not svc._model_loaded:
        print("\nInsightFace model not loaded — gallery images saved but NOT embedded.")
        print("Install: pip install insightface onnxruntime")
        print("Then re-run this script to generate embeddings.\n")
        return

    count = svc.enroll_gallery()
    if count:
        print(f"\nEmbeddings enrolled for {count} demo members.")
        print(f"Embeddings saved to: {settings.face_embeddings_cache}")
    else:
        print("\nNo embeddings generated. Check gallery images.")


def main():
    print("=" * 60)
    print("SmartKUET Sentinel — LFW Demo Gallery Preparation")
    print("=" * 60)
    print(f"\nGallery dir : {GALLERY_DIR}")
    print(f"Dataset dir : {DATASET_DIR}\n")

    # 1. Fetch LFW
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    lfw = fetch_lfw(DATASET_DIR)
    print(f"LFW loaded: {lfw.images.shape[0]} images, "
          f"{len(lfw.target_names)} identities available\n")

    # 2. Save gallery images
    print(f"Selecting {NUM_MEMBERS} identities ({IMAGES_EACH} images each)...")
    mapping = save_gallery(lfw, GALLERY_DIR)

    print("\nDemo member mapping (console only — NOT written to any committed file):")
    for label, real_name in mapping.items():
        print(f"  {label} → {real_name}")

    print(f"\nGallery saved to: {GALLERY_DIR}")
    print("NOTE: Gallery images are gitignored. Do NOT commit them.\n")

    # 3. Enroll embeddings
    print("Enrolling face embeddings with InsightFace...")
    enroll_embeddings(GALLERY_DIR)

    print("\nDone. Start the API to use face verification:")
    print("  .venv\\Scripts\\python -m uvicorn api.main:app --host 127.0.0.1 --port 8002")
    print("  GET  http://127.0.0.1:8002/api/face/status")
    print("  GET  http://127.0.0.1:8002/api/face/demo-members")


if __name__ == "__main__":
    main()
