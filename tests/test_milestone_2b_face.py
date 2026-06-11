"""
tests/test_milestone_2b_face.py — Milestone 2B

Tests for open-source face verification prototype.
All tests are designed to pass WITHOUT requiring:
  - InsightFace model download
  - LFW dataset download
  - Any real face images

Uses mock embeddings and mocked imports where needed.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ── Phase 1: Documentation ────────────────────────────────────────────────────

def test_docs_prototype_file_exists():
    """Design doc must exist."""
    doc = PROJECT_ROOT / "docs" / "open_face_verification_prototype.md"
    assert doc.exists(), "docs/open_face_verification_prototype.md is missing"


def test_docs_mentions_lfw():
    """Doc must mention LFW dataset."""
    doc = PROJECT_ROOT / "docs" / "open_face_verification_prototype.md"
    content = doc.read_text(encoding="utf-8").lower()
    assert "lfw" in content or "labeled faces in the wild" in content


def test_docs_privacy_statement():
    """Doc must explicitly state no real KUET data is used."""
    doc = PROJECT_ROOT / "docs" / "open_face_verification_prototype.md"
    content = doc.read_text(encoding="utf-8").lower()
    assert "not real kuet" in content or "not using real kuet" in content


def test_docs_mentions_insightface():
    """Doc must reference InsightFace as the embedding engine."""
    doc = PROJECT_ROOT / "docs" / "open_face_verification_prototype.md"
    content = doc.read_text(encoding="utf-8").lower()
    assert "insightface" in content


# ── Phase 2: Gitignore safety ─────────────────────────────────────────────────

def test_gitignore_face_datasets():
    """data/face_datasets/* must be gitignored."""
    gi = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "data/face_datasets/*" in gi


def test_gitignore_face_embeddings():
    """data/face_embeddings/* must be gitignored."""
    gi = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "data/face_embeddings/*" in gi


def test_gitignore_demo_gallery():
    """data/demo_face_gallery/* must be gitignored."""
    gi = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "data/demo_face_gallery/*" in gi


def test_gitignore_insightface_cache():
    """.cache/insightface/ must be gitignored (covered by .cache/)."""
    gi = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".cache/" in gi or ".cache/insightface" in gi


# ── Phase 3: FaceVerificationResult dataclass ─────────────────────────────────

def test_face_verification_result_dataclass():
    """FaceVerificationResult must have all required fields."""
    from core.face_verification import FaceVerificationResult, FaceVerificationStatus
    result = FaceVerificationResult(
        status=FaceVerificationStatus.UNKNOWN_VISITOR,
        display_color="red",
        confidence=0.15,
        matched_member=None,
        instruction="Manual verification required.",
    )
    assert result.status == FaceVerificationStatus.UNKNOWN_VISITOR
    assert result.display_color == "red"
    assert result.confidence == 0.15
    assert result.matched_member is None
    d = result.to_dict()
    assert "status" in d
    assert "display_color" in d
    assert "confidence" in d
    assert "matched_member" in d
    assert "instruction" in d


def test_face_verification_status_values():
    """All required status codes must exist."""
    from core.face_verification import FaceVerificationStatus
    required = [
        "VERIFIED_KNOWN_MEMBER",
        "UNKNOWN_VISITOR",
        "LOW_CONFIDENCE",
        "NO_FACE_DETECTED",
        "MODEL_UNAVAILABLE",
        "GALLERY_EMPTY",
        "ERROR",
    ]
    for code in required:
        assert hasattr(FaceVerificationStatus, code), f"Missing status: {code}"


# ── Phase 4: Service — MODEL_UNAVAILABLE graceful fallback ────────────────────

def test_face_service_model_unavailable_when_insightface_missing(tmp_path):
    """Service must return MODEL_UNAVAILABLE when insightface is not installed."""
    from core.face_verification import FaceVerificationService, FaceVerificationStatus

    with patch.dict(sys.modules, {"insightface": None, "insightface.app": None}):
        svc = FaceVerificationService(
            gallery_dir=tmp_path / "gallery",
            embeddings_cache_path=tmp_path / "embeddings.npy",
        )
        assert not svc._model_loaded

        dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        result = svc.verify_frame(dummy_frame)
        assert result.status == FaceVerificationStatus.MODEL_UNAVAILABLE
        assert result.display_color == "grey"


def test_face_service_gallery_empty_when_no_gallery(tmp_path):
    """Service with model but no gallery returns GALLERY_EMPTY."""
    from core.face_verification import FaceVerificationService, FaceVerificationStatus

    svc = FaceVerificationService(
        gallery_dir=tmp_path / "empty_gallery",
        embeddings_cache_path=tmp_path / "embeddings.npy",
    )
    # Simulate model loaded but gallery empty
    svc._model_loaded = True
    svc._gallery_loaded = False
    svc._gallery_embeddings = {}

    dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    result = svc.verify_frame(dummy_frame)
    assert result.status == FaceVerificationStatus.GALLERY_EMPTY


# ── Phase 5: Cosine similarity logic ─────────────────────────────────────────

def test_cosine_similarity_identical():
    """Identical vectors should have similarity ~1.0."""
    from core.face_verification import _cosine_similarity
    v = np.random.rand(512).astype(np.float32)
    sim = _cosine_similarity(v, v)
    assert abs(sim - 1.0) < 1e-4


def test_cosine_similarity_orthogonal():
    """Orthogonal vectors should have similarity ~0."""
    from core.face_verification import _cosine_similarity
    a = np.array([1.0, 0.0, 0.0])
    b = np.array([0.0, 1.0, 0.0])
    sim = _cosine_similarity(a, b)
    assert abs(sim) < 1e-4


def test_verification_known_with_mock_embeddings(tmp_path):
    """Service must return VERIFIED_KNOWN_MEMBER when embeddings match."""
    from core.face_verification import FaceVerificationService, FaceVerificationStatus

    known_emb = np.random.rand(512).astype(np.float32)
    gallery = {"DemoMemberA": [known_emb]}
    emb_path = tmp_path / "embeddings.npy"
    np.save(str(emb_path), gallery)

    svc = FaceVerificationService(
        gallery_dir=tmp_path / "gallery",
        embeddings_cache_path=emb_path,
        threshold=0.40,
        low_confidence_threshold=0.30,
    )
    # Inject mock model that returns the known embedding
    svc._model_loaded = True
    svc._gallery_loaded = True
    svc._gallery_embeddings = gallery

    mock_face = MagicMock()
    mock_face.normed_embedding = known_emb
    mock_face.bbox = [0, 0, 100, 100]
    svc._app = MagicMock()
    svc._app.get.return_value = [mock_face]

    dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    result = svc.verify_frame(dummy_frame)
    assert result.status == FaceVerificationStatus.VERIFIED_KNOWN_MEMBER
    assert result.matched_member == "DemoMemberA"
    assert result.confidence >= 0.99


def test_verification_unknown_with_mock_embeddings(tmp_path):
    """Service must return UNKNOWN_VISITOR when embeddings do not match."""
    from core.face_verification import FaceVerificationService, FaceVerificationStatus

    known_emb  = np.array([1.0] + [0.0] * 511, dtype=np.float32)
    unknown_emb = np.array([0.0, 1.0] + [0.0] * 510, dtype=np.float32)
    gallery = {"DemoMemberA": [known_emb]}

    emb_path = tmp_path / "embeddings.npy"
    np.save(str(emb_path), gallery)

    svc = FaceVerificationService(
        gallery_dir=tmp_path / "gallery",
        embeddings_cache_path=emb_path,
        threshold=0.40,
        low_confidence_threshold=0.30,
    )
    svc._model_loaded = True
    svc._gallery_loaded = True
    svc._gallery_embeddings = gallery

    mock_face = MagicMock()
    mock_face.normed_embedding = unknown_emb
    mock_face.bbox = [0, 0, 100, 100]
    svc._app = MagicMock()
    svc._app.get.return_value = [mock_face]

    dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    result = svc.verify_frame(dummy_frame)
    assert result.status == FaceVerificationStatus.UNKNOWN_VISITOR
    assert result.matched_member is None


# ── Phase 6: API routes ───────────────────────────────────────────

@pytest.fixture
def client():
    """Test client with InsightFace model loading patched to avoid download."""
    from fastapi.testclient import TestClient
    from core.face_verification import FaceVerificationService

    def _no_model_load(self):
        # Simulate model not installed — clean graceful fallback, no download
        self._model_loaded = False
        self._app = None

    with patch.object(FaceVerificationService, '_try_load_model', _no_model_load):
        from api.main import app
        with TestClient(app) as c:
            yield c


def test_api_face_status_returns_200(client):
    resp = client.get("/api/face/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "model_loaded" in data
    assert "gallery_loaded" in data


def test_api_face_demo_members_returns_200(client):
    resp = client.get("/api/face/demo-members")
    assert resp.status_code == 200
    data = resp.json()
    assert "members" in data
    assert "count" in data
    assert isinstance(data["members"], list)


def test_api_face_verify_image_rejects_traversal(client):
    """Path traversal attack must be rejected with 403."""
    resp = client.post("/api/face/verify-image", json={"image_path": "../../etc/passwd"})
    assert resp.status_code in (403, 404)


def test_api_face_verify_image_requires_body(client):
    """Missing image_path must return 400."""
    resp = client.post("/api/face/verify-image", json={})
    assert resp.status_code == 400


# ── Phase 7: Existing tests not broken ───────────────────────────────────────

def test_existing_config_loads():
    """Config must load cleanly with face verification fields."""
    from core.config import settings
    assert settings.face_gallery_dir is not None
    assert settings.face_embeddings_cache is not None
    assert 0.0 < settings.face_verification_threshold <= 1.0
    assert settings.face_model_name == "buffalo_s"
