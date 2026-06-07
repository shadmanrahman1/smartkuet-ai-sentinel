from core.video_processor import VideoProcessor


class StubCamera:
    @property
    def latest_frame(self):
        return None


def test_video_processor_status_without_model_or_camera():
    processor = VideoProcessor(
        camera=StubCamera(),
        detector=None,
        enabled=False,
    )

    try:
        status = processor.get_status()
    finally:
        processor.release()

    expected = {
        "yolo_enabled",
        "model_path",
        "device",
        "selected_device",
        "processed_frames",
        "last_inference_ms",
        "avg_inference_ms",
        "effective_fps",
        "model_error",
        "latest_summary",
        "tracking_enabled",
        "tracker_type",
        "active_track_count",
        "total_tracks_seen",
        "active_tracks",
    }

    assert expected.issubset(status)
    assert status["yolo_enabled"] is False
    assert status["processed_frames"] == 0
