import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Union

import cv2


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.config import PROJECT_ROOT, settings
from core.detector import YOLODetector
from core.tracker import PersonTracker


def parse_source(source: str) -> Union[int, str]:
    if source.strip().isdigit():
        return int(source)
    path = Path(source)
    if not path.is_absolute() and not source.startswith(("http://", "https://", "rtsp://")):
        return str((PROJECT_ROOT / path).resolve())
    return source


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark SmartKUET YOLO detection.")
    parser.add_argument("--source", required=True, help="Webcam index, local video, IP URL, or RTSP URL.")
    parser.add_argument("--seconds", type=float, default=20.0)
    args = parser.parse_args()

    source = parse_source(args.source)
    capture = cv2.VideoCapture(source)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = settings.benchmark_output_dir / f"benchmark_{stamp}.json"
    sample_path = settings.benchmark_output_dir / f"sample_{stamp}.jpg"

    detector = YOLODetector(
        model_path=settings.yolo_model_path,
        conf=settings.yolo_conf,
        imgsz=settings.yolo_imgsz,
        device=settings.yolo_device,
    )
    tracker = PersonTracker(
        tracker_type=settings.tracker_type,
        max_age_seconds=settings.max_track_age_seconds,
        iou_threshold=settings.track_iou,
        person_class_name=settings.track_person_class_name,
        min_confidence=settings.track_conf,
    ) if settings.tracking_enabled else None

    report = {
        "source": args.source,
        "resolved_source": str(source),
        "model": str(settings.yolo_model_path),
        "requested_device": settings.yolo_device,
        "selected_device": detector.selected_device,
        "frame_count": 0,
        "processed_frame_count": 0,
        "average_inference_ms": None,
        "approximate_fps": None,
        "average_persons_detected": 0.0,
        "average_phones_detected": 0.0,
        "average_vehicles_detected": 0.0,
        "tracking_enabled": settings.tracking_enabled,
        "tracker_type": tracker.backend if tracker else None,
        "average_active_tracks": 0.0,
        "max_active_tracks": 0,
        "total_tracks_seen": 0,
        "error": None,
        "sample_image": None,
    }

    if not capture.isOpened():
        report["error"] = f"Could not open source: {args.source}"
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print_report(report, report_path)
        return 1

    inference_times: list[float] = []
    person_counts: list[int] = []
    phone_counts: list[int] = []
    vehicle_counts: list[int] = []
    active_track_counts: list[int] = []
    start_time = time.perf_counter()

    try:
        while time.perf_counter() - start_time < args.seconds:
            ok, frame = capture.read()
            if not ok:
                break

            report["frame_count"] += 1
            start_inference = time.perf_counter()
            detections = detector.detect(frame)
            inference_ms = (time.perf_counter() - start_inference) * 1000
            inference_times.append(inference_ms)
            summary = detector.summarize(detections)
            person_counts.append(summary["person_count"])
            phone_counts.append(summary["phone_count"])
            vehicle_counts.append(summary["vehicle_count"])
            if tracker is not None:
                tracker.update(frame, detections)
                tracker_status = tracker.get_status()
                active_track_counts.append(tracker_status["active_track_count"])
                report["max_active_tracks"] = max(
                    report["max_active_tracks"],
                    tracker_status["active_track_count"],
                )
                report["total_tracks_seen"] = tracker_status["total_tracks_seen"]
            report["processed_frame_count"] += 1

            if report["sample_image"] is None:
                annotated = detector.annotate(frame, detections)
                cv2.imwrite(str(sample_path), annotated)
                report["sample_image"] = str(sample_path.relative_to(PROJECT_ROOT))
    except Exception as exc:
        report["error"] = str(exc)
    finally:
        capture.release()

    elapsed = max(0.001, time.perf_counter() - start_time)
    if inference_times:
        report["average_inference_ms"] = sum(inference_times) / len(inference_times)
        report["approximate_fps"] = report["processed_frame_count"] / elapsed
        report["average_persons_detected"] = sum(person_counts) / len(person_counts)
        report["average_phones_detected"] = sum(phone_counts) / len(phone_counts)
        report["average_vehicles_detected"] = sum(vehicle_counts) / len(vehicle_counts)
        if active_track_counts:
            report["average_active_tracks"] = sum(active_track_counts) / len(active_track_counts)

    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print_report(report, report_path)
    return 0 if report["processed_frame_count"] else 1


def print_report(report: dict, report_path: Path) -> None:
    print(f"source: {report['source']}")
    print(f"model: {report['model']}")
    print(f"requested device: {report['requested_device']}")
    print(f"selected device: {report['selected_device']}")
    print(f"frame count: {report['frame_count']}")
    print(f"processed frame count: {report['processed_frame_count']}")
    print(f"average inference ms: {report['average_inference_ms']}")
    print(f"approximate FPS: {report['approximate_fps']}")
    print(f"average persons detected: {report['average_persons_detected']}")
    print(f"average phones detected: {report['average_phones_detected']}")
    print(f"average vehicles detected: {report['average_vehicles_detected']}")
    print(f"tracking enabled: {report['tracking_enabled']}")
    print(f"tracker type: {report['tracker_type']}")
    print(f"average active tracks: {report['average_active_tracks']}")
    print(f"max active tracks: {report['max_active_tracks']}")
    print(f"total tracks seen: {report['total_tracks_seen']}")
    print(f"report: {report_path}")
    print(f"sample image: {report['sample_image']}")
    if report["error"]:
        print(f"error: {report['error']}")


if __name__ == "__main__":
    raise SystemExit(main())
