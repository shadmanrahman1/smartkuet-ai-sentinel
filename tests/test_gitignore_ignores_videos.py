from pathlib import Path


def test_gitignore_ignores_sample_videos():
    path = Path(".gitignore")
    assert path.exists(), ".gitignore does not exist"
    lines = path.read_text(encoding="utf-8").splitlines()

    assert "sample_videos/*" in lines
    assert "!sample_videos/README.md" in lines
    assert "!sample_videos/ATTRIBUTION.md" in lines

    # Make sure video formats are not unignored
    for line in lines:
        if line.startswith("!") and "sample_videos/" in line:
            assert not any(
                ext in line
                for ext in [".mp4", ".avi", ".mov", ".mkv", ".webm"]
            ), f"Video format unignored in gitignore: {line}"
