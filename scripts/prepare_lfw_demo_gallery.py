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


GALLERY_DIR    = settings.face_gallery_dir
DATASET_DIR    = settings.data_dir / "face_datasets" / "lfw"
LFW_HOME       = DATASET_DIR / "lfw_home"
LFW_FUNNELED   = LFW_HOME / "lfw_funneled"     # 250×250 full-res face images
NUM_MEMBERS    = 3       # number of demo identities to enroll
IMAGES_EACH    = 3       # images per demo member (used for enrollment)
MIN_FACES      = 8       # minimum LFW images required per identity
MEMBER_LABELS  = ["DemoMemberA", "DemoMemberB", "DemoMemberC",
                   "DemoMemberD", "DemoMemberE"]


def fetch_lfw(data_home: Path) -> None:
    """Download LFW dataset via sklearn if not already present."""
    if LFW_FUNNELED.exists() and any(LFW_FUNNELED.iterdir()):
        print(f"LFW already downloaded at: {LFW_FUNNELED}")
        return

    print(f"Fetching LFW dataset ...")
    print(f"  Download/cache dir: {data_home}")
    print("  This may take a few minutes on first run (~200MB).\n")

    from sklearn.datasets import fetch_lfw_people
    # resize=1.0 to trigger full download; we use lfw_funneled dir directly
    fetch_lfw_people(
        data_home=str(data_home),
        min_faces_per_person=MIN_FACES,
        resize=1.0,
        color=True,
    )


def pick_identities(lfw_funneled_dir: Path) -> list[tuple[str, list[Path]]]:
    """
    Pick NUM_MEMBERS identities from lfw_funneled with at least MIN_FACES images.
    Returns list of (real_name, [image_paths]).
    """
    candidates = []
    for person_dir in sorted(lfw_funneled_dir.iterdir()):
        if not person_dir.is_dir():
            continue
        imgs = sorted(person_dir.glob("*.jpg"))
        if len(imgs) >= MIN_FACES:
            candidates.append((person_dir.name, imgs))

    # Sort by most images (most data = best gallery quality)
    candidates.sort(key=lambda x: len(x[1]), reverse=True)
    return candidates[:NUM_MEMBERS]


def save_gallery(identities: list[tuple[str, list[Path]]], gallery_dir: Path) -> dict[str, str]:
    """
    Copy IMAGES_EACH images for each selected identity into the gallery dir.
    Returns mapping {DemoMemberX: real_lfw_name} (for console display only).
    """
    import shutil as _sh

    if gallery_dir.exists():
        _sh.rmtree(gallery_dir)
    gallery_dir.mkdir(parents=True, exist_ok=True)

    mapping: dict[str, str] = {}
    for member_idx, (real_name, img_paths) in enumerate(identities):
        label = MEMBER_LABELS[member_idx]
        display_name = real_name.replace("_", " ")
        mapping[label] = display_name

        member_dir = gallery_dir / label
        member_dir.mkdir(parents=True, exist_ok=True)

        selected = img_paths[:IMAGES_EACH]
        for i, src in enumerate(selected):
            dst = member_dir / f"img_{i}.jpg"
            _sh.copy2(src, dst)

        print(f"  {label}: {len(selected)} images saved "
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
        print("\nNo embeddings generated. Check gallery images contain detectable faces.")


def main():
    print("=" * 60)
    print("SmartKUET Sentinel — LFW Demo Gallery Preparation")
    print("=" * 60)
    print(f"\nGallery dir : {GALLERY_DIR}")
    print(f"Dataset dir : {DATASET_DIR}\n")

    # 1. Fetch LFW (downloads if not already present)
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    fetch_lfw(LFW_HOME)

    if not LFW_FUNNELED.exists():
        print(f"ERROR: lfw_funneled not found at {LFW_FUNNELED}")
        print("Please re-run to trigger download.")
        sys.exit(1)

    # 2. Pick best identities from full-res lfw_funneled
    print(f"Selecting {NUM_MEMBERS} identities (>= {MIN_FACES} images each)...")
    identities = pick_identities(LFW_FUNNELED)
    if not identities:
        print("No suitable identities found. Try reducing MIN_FACES.")
        sys.exit(1)

    print(f"Found {len(identities)} suitable identities.\n")

    # 3. Save gallery images (250×250 full-res LFW images)
    print(f"Saving {IMAGES_EACH} images per member to gallery...")
    mapping = save_gallery(identities, GALLERY_DIR)

    print("\nDemo member mapping (console only — NOT written to any committed file):")
    for label, real_name in mapping.items():
        print(f"  {label} -> {real_name}")

    print(f"\nGallery saved to: {GALLERY_DIR}")
    print("NOTE: Gallery images are gitignored. Do NOT commit them.\n")

    # 4. Enroll embeddings with InsightFace
    print("Enrolling face embeddings with InsightFace...")
    enroll_embeddings(GALLERY_DIR)

    print("\nDone. Start the API to use face verification:")
    print("  .venv\\Scripts\\python -m uvicorn api.main:app --host 127.0.0.1 --port 8002")
    print("  GET  http://127.0.0.1:8002/api/face/status")
    print("  GET  http://127.0.0.1:8002/api/face/demo-members")


if __name__ == "__main__":
    main()
