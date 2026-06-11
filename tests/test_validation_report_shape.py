from scripts.validate_demo_video import build_report_data


def test_build_report_data_shape():
    report = build_report_data(
        source="sample_videos/demo.mp4",
        resolved_source="/absolute/path/sample_videos/demo.mp4",
        seconds=10.0,
        total_frames_read=100,
        processed_frames=33,
        inference_times=[15.0, 20.0, 25.0],
        person_counts=[1, 2, 1],
        phone_counts=[0, 0, 1],
        vehicle_counts=[0, 1, 0],
        max_active_tracks=2,
        total_tracks_seen=3,
        total_security_events=2,
        event_count_by_type={"LOITERING": 1, "CROWDING": 1},
        event_count_by_level={"yellow": 2},
        highest_level_seen="yellow",
        real_elapsed=5.0,
    )

    assert report["source"] == "sample_videos/demo.mp4"
    assert report["resolved_source"] == "/absolute/path/sample_videos/demo.mp4"
    assert report["duration_seconds"] == 10.0
    assert report["total_frames_read"] == 100
    assert report["processed_frames"] == 33
    assert report["average_inference_ms"] == 20.0
    assert report["approximate_fps"] == 20.0
    assert report["average_person_count"] == 1.33
    assert report["average_phone_count"] == 0.33
    assert report["average_vehicle_count"] == 0.33
    assert report["max_active_tracks"] == 2
    assert report["total_tracks_seen"] == 3
    assert report["total_security_events"] == 2
    assert report["event_count_by_type"] == {"LOITERING": 1, "CROWDING": 1}
    assert report["event_count_by_level"] == {"yellow": 2}
    assert report["highest_security_level_seen"] == "yellow"
    assert "timestamp" in report
