from core.tracker import PersonTracker, bbox_iou


def person_detection(bbox, confidence=0.9):
    return {
        "class_name": "person",
        "confidence": confidence,
        "bbox": bbox,
    }


def test_bbox_iou_overlap():
    assert bbox_iou([0, 0, 100, 100], [10, 10, 110, 110]) > 0.5
    assert bbox_iou([0, 0, 100, 100], [200, 200, 300, 300]) == 0.0


def test_tracker_reuses_track_for_close_bbox():
    tracker = PersonTracker(iou_threshold=0.4)

    first = tracker.update(None, [person_detection([0, 0, 100, 100])])
    second = tracker.update(None, [person_detection([8, 8, 108, 108])])

    assert first[0]["track_id"] == second[0]["track_id"]
    assert tracker.get_status()["total_tracks_seen"] == 1


def test_tracker_creates_new_track_for_far_bbox():
    tracker = PersonTracker(iou_threshold=0.5)

    first = tracker.update(None, [person_detection([0, 0, 100, 100])])
    second = tracker.update(None, [person_detection([220, 220, 320, 320])])

    assert first[0]["track_id"] != second[0]["track_id"]
    assert tracker.get_status()["total_tracks_seen"] == 2
