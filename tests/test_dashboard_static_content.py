from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def test_dashboard_index_has_offline_and_human_in_the_loop_labels():
    index_path = PROJECT_ROOT / "dashboard" / "index.html"
    assert index_path.exists()
    
    content = index_path.read_text(encoding="utf-8")
    assert "SmartKUET Sentinel" in content
    assert "Offline Edge-AI Campus Security" in content
    assert "human-in-the-loop" in content.lower()
    assert "temporary track ids" in content.lower()
    assert "no cloud dependency" in content.lower()

def test_guard_view_has_decision_assistant_and_disclaimer():
    guard_path = PROJECT_ROOT / "dashboard" / "guard.html"
    assert guard_path.exists()
    
    content = guard_path.read_text(encoding="utf-8")
    assert "Guard Interface" in content
    assert "human-in-the-loop" in content.lower()
    assert "does not automatically approve or deny" in content.lower()
    assert "allow" in content.lower()
    assert "deny" in content.lower()

def test_examiner_view_has_mock_signal_and_assistant_disclaimer():
    exam_path = PROJECT_ROOT / "dashboard" / "exam.html"
    assert exam_path.exists()
    
    content = exam_path.read_text(encoding="utf-8")
    assert "Examiner View" in content
    assert "future module / mock signal" in content.lower()
    assert "only assists invigilators" in content.lower()
