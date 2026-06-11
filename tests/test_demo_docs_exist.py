from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def test_runbook_exists_and_contains_checklist_and_safety_terms():
    runbook_path = PROJECT_ROOT / "docs" / "demo_runbook.md"
    assert runbook_path.exists()
    
    content = runbook_path.read_text(encoding="utf-8")
    assert "demo.mp4" in content
    assert "print_demo_checklist.py" in content
    assert "validate_demo_video.py" in content
    assert "uvicorn" in content
    assert "privacy" in content.lower()
    assert "attribution" in content.lower()

def test_submission_pitch_exists_and_contains_truthful_sentinel_details():
    pitch_path = PROJECT_ROOT / "docs" / "submission_pitch.md"
    assert pitch_path.exists()
    
    content = pitch_path.read_text(encoding="utf-8")
    assert "SmartKUET Sentinel" in content
    assert "Offline Edge-AI" in content
    assert "no face recognition" in content.lower() or "no face identification" in content.lower()
    assert "human-in-the-loop" in content.lower()
    assert "yolov8n" in content.lower()
