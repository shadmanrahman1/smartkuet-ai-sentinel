from core.detector import YOLODetector


def test_detector_summary_counts_security_classes():
    detections = [
        {"class_name": "person", "confidence": 0.91, "bbox": [0, 0, 10, 10]},
        {"class_name": "person", "confidence": 0.86, "bbox": [10, 10, 20, 20]},
        {"class_name": "cell phone", "confidence": 0.72, "bbox": [5, 5, 12, 12]},
        {"class_name": "car", "confidence": 0.88, "bbox": [30, 30, 60, 60]},
        {"class_name": "motorcycle", "confidence": 0.77, "bbox": [80, 40, 120, 90]},
        {"class_name": "backpack", "confidence": 0.69, "bbox": [15, 25, 40, 55]},
    ]

    summary = YOLODetector.summarize(detections)

    assert summary["total"] == 6
    assert summary["person_count"] == 2
    assert summary["phone_count"] == 1
    assert summary["vehicle_count"] == 2
    assert summary["classes"]["backpack"] == 1


def test_detector_constructor_does_not_load_model(tmp_path):
    detector = YOLODetector(model_path=tmp_path / "yolov8n.pt")

    assert detector._model is None
