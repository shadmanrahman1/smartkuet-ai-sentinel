from core.tracker import PersonTracker
from core.video_processor import VideoProcessor


class StubCamera:
    @property
    def latest_frame(self):
        return None


def test_video_processor_status_includes_tracking_keys():
    tracker = PersonTracker()
    processor = VideoProcessor(
        camera=StubCamera(),
        detector=None,
        tracker=tracker,
        enabled=False,
        tracking_enabled=True,
    )

    try:
        status = processor.get_status()
    finally:
        processor.release()

    assert status["tracking_enabled"] is True
    assert status["tracker_type"] in {"iou_fallback", None}
    assert status["active_track_count"] == 0
    assert status["total_tracks_seen"] == 0
    assert status["active_tracks"] == []
