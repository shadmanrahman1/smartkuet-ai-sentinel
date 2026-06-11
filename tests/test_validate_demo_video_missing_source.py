import subprocess
import sys


def test_validate_demo_video_missing_source_graceful():
    result = subprocess.run(
        [
            sys.executable,
            "scripts/validate_demo_video.py",
            "--source",
            "sample_videos/non_existent.mp4",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "INSTRUCTION: The demo video file was not found." in result.stdout
    assert result.returncode == 0
