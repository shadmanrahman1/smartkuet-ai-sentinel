import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
import time
from typing import Any, Union

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.config import settings
from core.detector import YOLODetector
from core.security_rules import LEVEL_PRIORITY, SecurityRulesEngine
from core.tracker import PersonTracker


def parse_source(source: str) -> Union[int, str]:
    if source.strip().isdigit():
        return int(source)
    path = Path(source)
    if (
        not path.is_absolute()
        and not source.startswith(("http://", "https://", "rtsp://"))
    ):
        return str((PROJECT_ROOT / path).resolve())
    return source


def get_track_color(track_id: int) -> tuple[int, int, int]:
    palette = [
        (52, 211, 153),
        (56, 189, 248),
        (251, 191, 36),
        (248, 113, 113),
        (167, 139, 250),
    ]
    return palette[(track_id - 1) % len(palette)]


def annotate_frame_with_tracking(
    frame: np.ndarray,
    detections: list[dict[str, Any]],
    active_tracks: list[dict[str, Any]],
    detector: YOLODetector,
) -> np.ndarray:
    non_person_detections = [
        detection
        for detection in detections
        if detection.get("class_name") != "person"
    ]
    annotated = detector.annotate(frame, non_person_detections)

    for track in active_tracks:
        x1, y1, x2, y2 = [int(value) for value in track["bbox"]]
        track_id = int(track["track_id"])
        color = get_track_color(track_id)
        label = f"ID {track_id} | person | {float(track['confidence']):.2f}"
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 3)
        label_y = max(y1 - 10, 22)
        cv2.putText(
            annotated,
            label,
            (x1, label_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62,
            color,
            2,
            cv2.LINE_AA,
        )
    return annotated


def build_report_data(
    source: str,
    resolved_source: str,
    seconds: float,
    total_frames_read: int,
    processed_frames: int,
    inference_times: list[float],
    person_counts: list[int],
    phone_counts: list[int],
    vehicle_counts: list[int],
    max_active_tracks: int,
    total_tracks_seen: int,
    total_security_events: int,
    event_count_by_type: dict[str, int],
    event_count_by_level: dict[str, int],
    highest_level_seen: str,
    real_elapsed: float,
) -> dict[str, Any]:
    avg_inference = (
        sum(inference_times) / len(inference_times) if inference_times else 0.0
    )
    approx_fps = total_frames_read / real_elapsed if real_elapsed > 0 else 0.0
    avg_person = sum(person_counts) / len(person_counts) if person_counts else 0.0
    avg_phone = sum(phone_counts) / len(phone_counts) if phone_counts else 0.0
    avg_vehicle = (
        sum(vehicle_counts) / len(vehicle_counts) if vehicle_counts else 0.0
    )

    return {
        "timestamp": datetime.now().isoformat(),
        "source": source,
        "resolved_source": str(resolved_source),
        "duration_seconds": seconds,
        "total_frames_read": total_frames_read,
        "processed_frames": processed_frames,
        "average_inference_ms": round(avg_inference, 2),
        "approximate_fps": round(approx_fps, 2),
        "average_person_count": round(avg_person, 2),
        "average_phone_count": round(avg_phone, 2),
        "average_vehicle_count": round(avg_vehicle, 2),
        "max_active_tracks": max_active_tracks,
        "total_tracks_seen": total_tracks_seen,
        "total_security_events": total_security_events,
        "event_count_by_type": event_count_by_type,
        "event_count_by_level": event_count_by_level,
        "highest_security_level_seen": highest_level_seen,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate SmartKUET YOLO + tracking + rules on local video."
    )
    parser.add_argument(
        "--source",
        default="sample_videos/demo.mp4",
        help="Path to local video file or camera source.",
    )
    parser.add_argument("--seconds", type=float, default=30.0)
    args = parser.parse_args()

    resolved_source = parse_source(args.source)
    is_file_source = False
    if isinstance(resolved_source, str) and not resolved_source.startswith(
        ("http://", "https://", "rtsp://")
    ):
        is_file_source = True

    if is_file_source and not Path(resolved_source).exists():
        print("=" * 80)
        print("INSTRUCTION: The demo video file was not found.")
        print(f"Please place a local video file at: {args.source}")
        print("or specify a valid video file with --source <path_to_video>.")
        print("=" * 80)
        return 0

    capture = cv2.VideoCapture(resolved_source)
    if not capture.isOpened():
        print("=" * 80)
        print("INSTRUCTION: Could not open the specified video source.")
        print(f"Source: {args.source}")
        print("Please place a local video file at sample_videos/demo.mp4")
        print("and ensure it is a valid, uncorrupted video.")
        print("=" * 80)
        capture.release()
        return 0

    # Initialize directory paths
    settings.benchmark_output_dir.mkdir(parents=True, exist_ok=True)
    validation_frames_dir = settings.video_output_dir / "validation_frames"
    validation_frames_dir.mkdir(parents=True, exist_ok=True)

    detector = YOLODetector(
        model_path=settings.yolo_model_path,
        conf=settings.yolo_conf,
        imgsz=settings.yolo_imgsz,
        device=settings.yolo_device,
    )
    tracker = (
        PersonTracker(
            tracker_type=settings.tracker_type,
            max_age_seconds=settings.max_track_age_seconds,
            iou_threshold=settings.track_iou,
            person_class_name=settings.track_person_class_name,
            min_confidence=settings.track_conf,
        )
        if settings.tracking_enabled
        else None
    )
    security_rules = SecurityRulesEngine(
        rules_enabled=settings.security_rules_enabled,
        normal_start_hour=settings.security_normal_start_hour,
        normal_end_hour=settings.security_normal_end_hour,
        crowding_person_threshold=settings.crowding_person_threshold,
        loiter_seconds=settings.loiter_seconds,
        event_cooldown_seconds=settings.security_event_cooldown_seconds,
        high_risk_cooldown_seconds=settings.security_high_risk_cooldown_seconds,
        location=settings.security_location,
    )

    total_video_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    video_fps = capture.get(cv2.CAP_PROP_FPS)
    if video_fps <= 0:
        video_fps = 30.0
    max_frames_to_read = int(video_fps * args.seconds)

    if total_video_frames > 0:
        frames_to_process = min(total_video_frames, max_frames_to_read)
    else:
        frames_to_process = max_frames_to_read

    save_indices = []
    if frames_to_process >= 3:
        save_indices = [
            max(0, frames_to_process // 10),
            max(1, frames_to_process // 2),
            max(2, int(frames_to_process * 0.9)),
        ]
    elif frames_to_process == 2:
        save_indices = [0, 1]
    elif frames_to_process == 1:
        save_indices = [0]
    save_indices = sorted(list(set(save_indices)))

    total_frames_read = 0
    processed_frames = 0
    inference_times = []
    person_counts = []
    phone_counts = []
    vehicle_counts = []
    active_track_counts = []
    max_active_tracks = 0
    total_tracks_seen = 0
    total_security_events = 0
    event_count_by_type = {}
    event_count_by_level = {}
    highest_level_seen = "green"

    start_time = time.perf_counter()

    try:
        while True:
            # Enforce the duration constraint
            elapsed_time = time.perf_counter() - start_time
            if elapsed_time >= args.seconds:
                break

            ok, frame = capture.read()
            if not ok:
                break

            total_frames_read += 1
            should_detect = (
                total_frames_read % settings.detection_every_n_frames == 0
            ) or (total_frames_read == 1)

            if should_detect:
                start_inf = time.perf_counter()
                detections = detector.detect(frame)
                inf_ms = (time.perf_counter() - start_inf) * 1000
                inference_times.append(inf_ms)
                processed_frames += 1

                if tracker is not None:
                    tracker.update(frame, detections)
                    tracker_status = tracker.get_status()
                    active_tracks = tracker_status["active_tracks"]
                    active_track_count = tracker_status["active_track_count"]
                    total_tracks_seen = tracker_status["total_tracks_seen"]
                else:
                    active_tracks = []
                    active_track_count = 0
                    total_tracks_seen = 0

                summary = detector.summarize(detections)
                person_counts.append(summary["person_count"])
                phone_counts.append(summary["phone_count"])
                vehicle_counts.append(summary["vehicle_count"])
                active_track_counts.append(active_track_count)
                max_active_tracks = max(max_active_tracks, active_track_count)
            else:
                if tracker is not None:
                    # Update tracker with empty/cached detections to age existing tracks
                    tracker_status = tracker.get_status()
                    active_tracks = tracker_status["active_tracks"]
                    active_track_count = tracker_status["active_track_count"]
                else:
                    active_tracks = []
                    active_track_count = 0

            # Evaluate security rules on every frame
            if tracker is not None:
                tracking_summary_dict = tracker.get_status()
            else:
                tracking_summary_dict = {
                    "enabled": False,
                    "tracker_type": None,
                    "active_track_count": 0,
                    "total_tracks_seen": 0,
                    "active_tracks": [],
                    "error": None,
                }

            if "summary" not in locals():
                summary = detector.summarize([])

            camera_status_dict = {
                "source": args.source,
                "source_type": "validation",
                "is_opened": True,
                "frame_count": total_frames_read,
                "width": int(frame.shape[1]),
                "height": int(frame.shape[0]),
                "fps_estimate": None,
                "last_error": None,
            }

            events = security_rules.evaluate(
                tracking_summary=tracking_summary_dict,
                detection_summary=summary,
                camera_status=camera_status_dict,
            )

            for event in events:
                event_type = event["event_type"]
                level = event["level"]
                event_count_by_type[event_type] = (
                    event_count_by_type.get(event_type, 0) + 1
                )
                event_count_by_level[level] = (
                    event_count_by_level.get(level, 0) + 1
                )
                total_security_events += 1
                if LEVEL_PRIORITY.get(level, 0) > LEVEL_PRIORITY.get(
                    highest_level_seen, 0
                ):
                    highest_level_seen = level

            # Save annotated frame if this index matches save indices
            current_frame_idx = total_frames_read - 1
            if current_frame_idx in save_indices:
                if tracker is not None:
                    annotated = annotate_frame_with_tracking(
                        frame,
                        detections if "detections" in locals() else [],
                        active_tracks,
                        detector,
                    )
                else:
                    annotated = detector.annotate(
                        frame, detections if "detections" in locals() else []
                    )

                frame_path = (
                    validation_frames_dir / f"frame_{total_frames_read:04d}.jpg"
                )
                cv2.imwrite(str(frame_path), annotated)

    except Exception as exc:
        print(f"Error during validation loop: {exc}")
    finally:
        capture.release()

    real_elapsed = max(0.001, time.perf_counter() - start_time)

    report = build_report_data(
        source=args.source,
        resolved_source=str(resolved_source),
        seconds=args.seconds,
        total_frames_read=total_frames_read,
        processed_frames=processed_frames,
        inference_times=inference_times,
        person_counts=person_counts,
        phone_counts=phone_counts,
        vehicle_counts=vehicle_counts,
        max_active_tracks=max_active_tracks,
        total_tracks_seen=total_tracks_seen,
        total_security_events=total_security_events,
        event_count_by_type=event_count_by_type,
        event_count_by_level=event_count_by_level,
        highest_level_seen=highest_level_seen,
        real_elapsed=real_elapsed,
    )

    # Save JSON report
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = (
        settings.benchmark_output_dir / f"validation_{stamp}.json"
    )
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # Print validation report to console
    print("\n====================================================")
    print("               VALIDATION REPORT SUMMARY             ")
    print("====================================================")
    print(f"Report saved to:             {report_path}")
    print(f"Total frames read:           {total_frames_read}")
    print(f"Processed frames (YOLO run): {processed_frames}")
    print(f"Approximate FPS:             {report['approximate_fps']}")
    print(f"Average inference:           {report['average_inference_ms']} ms")
    print(f"Average person count:        {report['average_person_count']}")
    print(f"Average phone count:         {report['average_phone_count']}")
    print(f"Average vehicle count:       {report['average_vehicle_count']}")
    print(f"Max active tracks:           {report['max_active_tracks']}")
    print(f"Total tracks seen:           {report['total_tracks_seen']}")
    print(f"Total security events:       {report['total_security_events']}")
    print(f"Event counts by level:       {report['event_count_by_level']}")
    print(f"Event counts by type:        {report['event_count_by_type']}")
    print(f"Highest security level:      {report['highest_security_level_seen']}")
    print("====================================================\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
