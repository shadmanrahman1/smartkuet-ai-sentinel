from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def test_submission_documents_exist():
    docs = [
        "final_submission_pack.md",
        "demo_script.md",
        "judges_qna.md",
        "technical_architecture.md"
    ]
    for doc in docs:
        doc_path = PROJECT_ROOT / "docs" / doc
        assert doc_path.exists(), f"Missing expected submission doc: {doc}"

def test_final_submission_pack_content_safety():
    pack_path = PROJECT_ROOT / "docs" / "final_submission_pack.md"
    content = pack_path.read_text(encoding="utf-8").lower()
    assert "human-in-the-loop" in content
    assert "does not identify students" in content

def test_demo_script_content_branding():
    script_path = PROJECT_ROOT / "docs" / "demo_script.md"
    content = script_path.read_text(encoding="utf-8")
    assert "SmartKUET Sentinel" in content

def test_judges_qna_content_offline_safety():
    qna_path = PROJECT_ROOT / "docs" / "judges_qna.md"
    content = qna_path.read_text(encoding="utf-8").lower()
    assert "without internet" in content

def test_technical_architecture_content_layers():
    arch_path = PROJECT_ROOT / "docs" / "technical_architecture.md"
    content = arch_path.read_text(encoding="utf-8")
    assert "YOLO" in content
    assert "SQLite" in content
