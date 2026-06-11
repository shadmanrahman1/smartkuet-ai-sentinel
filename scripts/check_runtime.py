from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.config import get_runtime_info, settings


def main() -> None:
    runtime = get_runtime_info()
    paths: dict[str, Path] = {
        "model_dir": settings.model_dir,
        "runs_dir": settings.runs_dir,
        "benchmark_output_dir": settings.benchmark_output_dir,
        "tracking_output_dir": settings.tracking_output_dir,
        "video_output_dir": settings.video_output_dir,
        "data_dir": settings.data_dir,
        "snapshot_dir": settings.snapshot_dir,
        "evidence_dir": settings.evidence_dir,
        "sample_video_dir": settings.sample_video_dir,
        "cache_dir": settings.cache_dir,
    }

    print(f"Python version: {runtime['python_version']}")
    print(f"Platform: {runtime['platform']}")
    print(f"OpenCV version: {runtime['opencv_version']}")
    print(f"Torch available: {runtime['torch_available']}")
    print(f"Torch version: {runtime['torch_version']}")
    print(f"CUDA available: {runtime['cuda_available']}")
    print(f"CUDA version: {runtime['cuda_version']}")
    print(f"CUDA device count: {runtime['cuda_device_count']}")
    print(f"CUDA device name: {runtime['cuda_device_name']}")
    print(f"Ultralytics available: {runtime['ultralytics_available']}")
    print(f"YOLO model path: {settings.yolo_model_path}")
    print(f"YOLO model exists: {settings.yolo_model_path.exists()}")
    print(f"TRACKING_ENABLED: {settings.tracking_enabled}")
    print(f"TRACKER_TYPE: {settings.tracker_type}")
    print(f"TRACKING_OUTPUT_DIR: {settings.tracking_output_dir}")
    print(f"TRACKING_OUTPUT_DIR exists: {settings.tracking_output_dir.exists()}")
    print(f"SECURITY_RULES_ENABLED: {settings.security_rules_enabled}")
    print(f"SECURITY_LOCATION: {settings.security_location}")
    print(f"SECURITY_NORMAL_HOURS: {settings.security_normal_start_hour}-{settings.security_normal_end_hour}")
    print(f"CROWDING_PERSON_THRESHOLD: {settings.crowding_person_threshold}")
    print(f"LOITER_SECONDS: {settings.loiter_seconds}")
    print(f"SECURITY_EVENT_COOLDOWN_SECONDS: {settings.security_event_cooldown_seconds}")
    print(f"SECURITY_HIGH_RISK_COOLDOWN_SECONDS: {settings.security_high_risk_cooldown_seconds}")
    print(f"SECURITY_SAVE_EVENT_SNAPSHOT: {settings.security_save_event_snapshot}")
    print(f"GATE_ZONE_ENABLED: {settings.gate_zone_enabled}")
    if settings.gate_zone_enabled:
        print(f"GATE_ZONE_ROI (normalized): x1={settings.gate_zone_x1} y1={settings.gate_zone_y1} x2={settings.gate_zone_x2} y2={settings.gate_zone_y2}")
    print(f"MAX_TRACK_MISSED_FRAMES: {settings.max_track_missed_frames}")
    print("Project runtime directories:")
    for name, path in paths.items():
        print(f"  {name}: {path} exists={path.exists()}")


if __name__ == "__main__":
    main()
