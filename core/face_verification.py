"""
core/face_verification.py — Milestone 2B

Open-source face verification prototype using InsightFace + LFW demo gallery.

Privacy notice:
  - No real KUET data. Gallery contains open-source LFW demo identities only.
  - Labels shown as "Demo Member A/B/C" — never real identity names.
  - All decisions are advisory. Human guard makes final gate-control choices.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

# ── Status codes ────────────────────────────────────────────────────────────

class FaceVerificationStatus(str, Enum):
    VERIFIED_KNOWN_MEMBER = "VERIFIED_KNOWN_MEMBER"
    UNKNOWN_VISITOR       = "UNKNOWN_VISITOR"
    LOW_CONFIDENCE        = "LOW_CONFIDENCE"
    NO_FACE_DETECTED      = "NO_FACE_DETECTED"
    MODEL_UNAVAILABLE     = "MODEL_UNAVAILABLE"
    GALLERY_EMPTY         = "GALLERY_EMPTY"
    ERROR                 = "ERROR"


DISPLAY_COLOR = {
    FaceVerificationStatus.VERIFIED_KNOWN_MEMBER: "green",
    FaceVerificationStatus.UNKNOWN_VISITOR:        "red",
    FaceVerificationStatus.LOW_CONFIDENCE:         "yellow",
    FaceVerificationStatus.NO_FACE_DETECTED:       "grey",
    FaceVerificationStatus.MODEL_UNAVAILABLE:      "grey",
    FaceVerificationStatus.GALLERY_EMPTY:          "grey",
    FaceVerificationStatus.ERROR:                  "grey",
}

INSTRUCTIONS = {
    FaceVerificationStatus.VERIFIED_KNOWN_MEMBER: "Identity matches a known demo member. Guard may allow entry.",
    FaceVerificationStatus.UNKNOWN_VISITOR:        "Identity does not match any enrolled member. Manual verification required.",
    FaceVerificationStatus.LOW_CONFIDENCE:         "Low confidence match. Manual ID verification recommended.",
    FaceVerificationStatus.NO_FACE_DETECTED:       "No face detected in the provided image.",
    FaceVerificationStatus.MODEL_UNAVAILABLE:      "InsightFace model not loaded. Run: pip install insightface onnxruntime",
    FaceVerificationStatus.GALLERY_EMPTY:          "Demo gallery is empty. Run: python scripts/prepare_lfw_demo_gallery.py",
    FaceVerificationStatus.ERROR:                  "Verification error. Check logs.",
}


# ── Result dataclass ─────────────────────────────────────────────────────────

@dataclass
class FaceVerificationResult:
    status:         FaceVerificationStatus
    display_color:  str
    confidence:     float                    # cosine similarity, 0–1
    matched_member: Optional[str]            # "Demo Member A" etc, or None
    instruction:    str
    face_count:     int = 0
    processing_ms:  float = 0.0
    error_detail:   Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "status":         self.status.value,
            "display_color":  self.display_color,
            "confidence":     round(self.confidence, 4),
            "matched_member": self.matched_member,
            "instruction":    self.instruction,
            "face_count":     self.face_count,
            "processing_ms":  round(self.processing_ms, 2),
        }


# ── Helpers ──────────────────────────────────────────────────────────────────

def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two L2-normalised embedding vectors."""
    a = a / (np.linalg.norm(a) + 1e-8)
    b = b / (np.linalg.norm(b) + 1e-8)
    return float(np.dot(a, b))


def _make_result(status: FaceVerificationStatus, **kwargs) -> FaceVerificationResult:
    return FaceVerificationResult(
        status=status,
        display_color=DISPLAY_COLOR[status],
        instruction=INSTRUCTIONS[status],
        confidence=kwargs.get("confidence", 0.0),
        matched_member=kwargs.get("matched_member", None),
        face_count=kwargs.get("face_count", 0),
        processing_ms=kwargs.get("processing_ms", 0.0),
        error_detail=kwargs.get("error_detail", None),
    )


# ── Service ──────────────────────────────────────────────────────────────────

class FaceVerificationService:
    """
    Local face verification using InsightFace buffalo_s model.

    Enrolled gallery: open-source LFW demo identities labeled as
    'Demo Member A/B/C'. Not real KUET data.
    """

    def __init__(
        self,
        gallery_dir: Path,
        embeddings_cache_path: Path,
        insightface_cache_dir: Optional[Path] = None,
        model_name: str = "buffalo_s",
        threshold: float = 0.40,
        low_confidence_threshold: float = 0.30,
    ):
        self.gallery_dir            = Path(gallery_dir)
        self.embeddings_cache_path  = Path(embeddings_cache_path)
        self.model_name             = model_name
        self.threshold              = threshold
        self.low_confidence_threshold = low_confidence_threshold
        self.insightface_cache_dir  = Path(insightface_cache_dir) if insightface_cache_dir else None

        self._app               = None   # InsightFace FaceAnalysis app
        self._gallery_embeddings: dict[str, list[np.ndarray]] = {}
        self._model_loaded      = False
        self._gallery_loaded    = False

        # Attempt to load
        self._try_load_model()
        if self._model_loaded:
            self._try_load_gallery()

    # ── Model loading ────────────────────────────────────────────────────────

    def _try_load_model(self) -> None:
        """Load InsightFace model. Sets self._model_loaded = False on any failure."""
        try:
            import insightface
            from insightface.app import FaceAnalysis

            providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]

            kwargs: dict = {"name": self.model_name, "providers": providers}
            if self.insightface_cache_dir:
                os.environ["INSIGHTFACE_HOME"] = str(self.insightface_cache_dir.parent)
                self.insightface_cache_dir.mkdir(parents=True, exist_ok=True)

            self._app = FaceAnalysis(**kwargs)
            self._app.prepare(ctx_id=0, det_size=(640, 640))
            self._model_loaded = True
            logger.info("FaceVerificationService: InsightFace '%s' loaded.", self.model_name)

        except ImportError:
            logger.warning(
                "FaceVerificationService: insightface not installed. "
                "Run: pip install insightface onnxruntime"
            )
        except Exception as exc:
            logger.error("FaceVerificationService: model load failed: %s", exc)

    # ── Gallery management ───────────────────────────────────────────────────

    def _get_gallery_members(self) -> list[str]:
        """Return sorted list of member sub-directory names."""
        if not self.gallery_dir.exists():
            return []
        return sorted([
            d.name for d in self.gallery_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ])

    def _embed_image(self, image_path: Path) -> Optional[np.ndarray]:
        """Return 512-dim embedding for the largest face in image, or None."""
        try:
            import cv2
            bgr = cv2.imread(str(image_path))
            if bgr is None:
                return None
            faces = self._app.get(bgr)
            if not faces:
                return None
            # Pick the face with largest bounding box area
            best = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
            return best.normed_embedding
        except Exception as exc:
            logger.debug("Embed failed for %s: %s", image_path, exc)
            return None

    def enroll_gallery(self) -> int:
        """
        Embed all images in the gallery directory and save .npy cache.
        Returns number of successfully enrolled members.
        """
        if not self._model_loaded:
            logger.warning("Cannot enroll: model not loaded.")
            return 0

        members = self._get_gallery_members()
        if not members:
            logger.warning("Gallery directory empty: %s", self.gallery_dir)
            return 0

        gallery: dict[str, list[np.ndarray]] = {}
        for member in members:
            member_dir = self.gallery_dir / member
            embeddings = []
            for img_path in sorted(member_dir.glob("*.jpg")) + sorted(member_dir.glob("*.png")):
                emb = self._embed_image(img_path)
                if emb is not None:
                    embeddings.append(emb)
            if embeddings:
                gallery[member] = embeddings
                logger.info("Enrolled '%s': %d embeddings.", member, len(embeddings))
            else:
                logger.warning("No valid faces found for member '%s'.", member)

        if gallery:
            self.embeddings_cache_path.parent.mkdir(parents=True, exist_ok=True)
            np.save(str(self.embeddings_cache_path), gallery)
            self._gallery_embeddings = gallery
            self._gallery_loaded = True
            logger.info("Gallery saved to %s (%d members).", self.embeddings_cache_path, len(gallery))

        return len(gallery)

    def _try_load_gallery(self) -> None:
        """Load gallery from .npy cache if it exists."""
        if not self.embeddings_cache_path.exists():
            logger.info("No gallery cache found at %s — run enroll_gallery().", self.embeddings_cache_path)
            return
        try:
            loaded = np.load(str(self.embeddings_cache_path), allow_pickle=True).item()
            self._gallery_embeddings = loaded
            self._gallery_loaded = bool(loaded)
            logger.info("Gallery loaded: %d members.", len(loaded))
        except Exception as exc:
            logger.error("Failed to load gallery cache: %s", exc)

    # ── Verification ─────────────────────────────────────────────────────────

    def _verify_embedding(self, query_emb: np.ndarray) -> tuple[str | None, float]:
        """
        Compare query embedding against all gallery embeddings.
        Returns (best_member_label, best_similarity).
        """
        best_member = None
        best_sim = -1.0
        for member, embeddings in self._gallery_embeddings.items():
            for enrolled_emb in embeddings:
                sim = _cosine_similarity(query_emb, enrolled_emb)
                if sim > best_sim:
                    best_sim = sim
                    best_member = member
        return best_member, best_sim

    def verify_frame(self, bgr_frame: np.ndarray) -> FaceVerificationResult:
        """
        Run face verification on a BGR numpy frame.
        Returns a FaceVerificationResult.
        """
        import time
        t0 = time.perf_counter()

        if not self._model_loaded:
            return _make_result(FaceVerificationStatus.MODEL_UNAVAILABLE)

        if not self._gallery_loaded or not self._gallery_embeddings:
            return _make_result(FaceVerificationStatus.GALLERY_EMPTY)

        try:
            faces = self._app.get(bgr_frame)
        except Exception as exc:
            return _make_result(FaceVerificationStatus.ERROR, error_detail=str(exc))

        ms = (time.perf_counter() - t0) * 1000

        if not faces:
            return _make_result(FaceVerificationStatus.NO_FACE_DETECTED, processing_ms=ms)

        # Use the largest face for verification
        best_face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
        query_emb = best_face.normed_embedding

        matched_member, similarity = self._verify_embedding(query_emb)

        if similarity >= self.threshold:
            return _make_result(
                FaceVerificationStatus.VERIFIED_KNOWN_MEMBER,
                confidence=similarity,
                matched_member=matched_member,
                face_count=len(faces),
                processing_ms=ms,
            )
        elif similarity >= self.low_confidence_threshold:
            return _make_result(
                FaceVerificationStatus.LOW_CONFIDENCE,
                confidence=similarity,
                matched_member=matched_member,
                face_count=len(faces),
                processing_ms=ms,
            )
        else:
            return _make_result(
                FaceVerificationStatus.UNKNOWN_VISITOR,
                confidence=similarity,
                face_count=len(faces),
                processing_ms=ms,
            )

    def verify_image_path(self, image_path: Path) -> FaceVerificationResult:
        """
        Run face verification on an image file path.
        Path must be under the project data/ directory (traversal protection).
        """
        try:
            import cv2
            bgr = cv2.imread(str(image_path))
            if bgr is None:
                return _make_result(
                    FaceVerificationStatus.ERROR,
                    error_detail=f"Could not read image: {image_path.name}",
                )
            return self.verify_frame(bgr)
        except Exception as exc:
            return _make_result(FaceVerificationStatus.ERROR, error_detail=str(exc))

    # ── Status ───────────────────────────────────────────────────────────────

    def get_status(self) -> dict:
        return {
            "model_loaded":     self._model_loaded,
            "model_name":       self.model_name,
            "gallery_loaded":   self._gallery_loaded,
            "gallery_members":  list(self._gallery_embeddings.keys()),
            "gallery_size":     len(self._gallery_embeddings),
            "threshold":        self.threshold,
            "low_confidence_threshold": self.low_confidence_threshold,
            "gallery_dir":      str(self.gallery_dir),
            "embeddings_cache": str(self.embeddings_cache_path),
        }

    def get_demo_members(self) -> list[str]:
        """Return list of enrolled demo member labels (no real identity names)."""
        return sorted(self._gallery_embeddings.keys())
