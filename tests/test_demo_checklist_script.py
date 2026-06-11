import subprocess
import sys


def test_demo_checklist_runs_without_crash():
    result = subprocess.run(
        [sys.executable, "scripts/print_demo_checklist.py"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "SMARTKUET DEMO CHECKLIST & STATUS" in result.stdout
