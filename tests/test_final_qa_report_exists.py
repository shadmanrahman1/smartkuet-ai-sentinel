from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def test_final_qa_report_exists_and_contains_safety_keywords():
    report_path = PROJECT_ROOT / "docs" / "final_qa_report.md"
    assert report_path.exists(), "docs/final_qa_report.md does not exist"
    
    content = report_path.read_text(encoding="utf-8").lower()
    assert "final repository qa" in content
    assert "human-in-the-loop" in content
    assert "does not identify students" in content
    assert "offline" in content
    assert "screenshot" in content
