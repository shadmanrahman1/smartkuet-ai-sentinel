from pathlib import Path


def test_attribution_file_exists():
    path = Path("sample_videos/ATTRIBUTION.md")
    assert path.exists(), "sample_videos/ATTRIBUTION.md does not exist"
    content = path.read_text(encoding="utf-8")
    assert "Intel IoT DevKit sample-videos" in content
    assert "CC-BY-4.0" in content
    assert "Do Not Commit Videos" in content
