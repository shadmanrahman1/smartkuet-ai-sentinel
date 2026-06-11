from pathlib import Path
from scripts.validate_demo_video import build_report_data, write_markdown_summary


def test_build_report_data_shape():
    report = build_report_data(
        source="sample_videos/demo.mp4",
        resolved_source="/absolute/path/sample_videos/demo.mp4",
        seconds=10.0,
        total_frames_read=100,
        processed_frames=33,
        inference_times=[1000.0, 150.0, 20.0, 25.0, 20.0],
        warmup_frames=2,
        person_counts=[1, 2, 1],
        phone_counts=[0, 0, 1],
        vehicle_counts=[0, 1, 0],
        max_active_tracks=2,
        total_tracks_seen=3,
        total_security_events=2,
        event_count_by_type={"LOITERING": 1, "CROWDING": 1},
        event_count_by_level={"yellow": 2},
        highest_security_level_seen="yellow",
        real_elapsed=5.0,
        saved_validation_frames=[
            "runs/videos/validation_frames/validation_sample_1.jpg"
        ],
        notes=["Test note"],
    )

    assert report["source"] == "sample_videos/demo.mp4"
    assert report["resolved_source"] == "/absolute/path/sample_videos/demo.mp4"
    assert report["duration_seconds"] == 10.0
    assert report["total_frames_read"] == 100
    assert report["processed_frames"] == 33
    assert report["warmup_frames"] == 2
    assert report["average_inference_ms_after_warmup"] == 21.67
    assert report["average_inference_ms"] == 21.67
    assert report["average_inference_ms_all"] == 243.0
    assert report["approximate_fps"] == 20.0
    assert report["average_person_count"] == 1.33
    assert report["average_phone_count"] == 0.33
    assert report["average_vehicle_count"] == 0.33
    assert report["max_active_tracks"] == 2
    assert report["total_tracks_seen"] == 3
    assert report["total_security_events"] == 2
    assert report["saved_validation_frames"] == [
        "runs/videos/validation_frames/validation_sample_1.jpg"
    ]
    assert report["saved_validation_frame_count"] == 1
    assert report["notes"] == ["Test note"]
    assert "timestamp" in report


def test_write_markdown_summary(tmp_path):
    report = {
        "source": "sample_videos/demo.mp4",
        "approximate_fps": 15.0,
        "average_inference_ms_after_warmup": 22.5,
        "average_inference_ms_all": 250.0,
        "average_person_count": 1.2,
        "max_active_tracks": 4,
        "total_tracks_seen": 5,
        "event_count_by_level": {"green": 50, "yellow": 2},
        "event_count_by_type": {"NORMAL_ACTIVITY": 50, "CROWDING": 2},
        "highest_security_level_seen": "yellow",
        "saved_validation_frames": [
            "runs/videos/validation_frames/validation_sample_1.jpg"
        ],
    }

    summary_path = tmp_path / "latest_validation_summary.md"
    write_markdown_summary(report, summary_path)

    assert summary_path.exists()
    content = summary_path.read_text(encoding="utf-8")
    assert "# Latest Validation Summary" in content
    assert "sample_videos/demo.mp4" in content
    assert "22.5 ms" in content
    assert "validation_sample_1.jpg" in content
    assert "Track IDs are temporary and do not identify people." in content
