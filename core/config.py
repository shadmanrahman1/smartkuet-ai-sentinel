import os
import platform
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Union

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def _project_path(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


def _camera_source(value: str) -> Union[int, str]:
    if value.strip().isdigit():
        return int(value)
    return value


def _bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str
    location: str
    camera_source: Union[int, str]
    database_path: Path
    cache_dir: Path
    model_dir: Path
    runs_dir: Path
    benchmark_output_dir: Path
    tracking_output_dir: Path
    data_dir: Path
    snapshot_dir: Path
    evidence_dir: Path
    sample_video_dir: Path
    video_output_dir: Path
    camera_reconnect_seconds: float
    camera_loop_video: bool
    yolo_enabled: bool
    yolo_model_path: Path
    yolo_conf: float
    yolo_imgsz: int
    yolo_device: str
    detection_every_n_frames: int
    tracking_enabled: bool
    tracker_type: str
    track_person_class_name: str
    track_conf: float
    track_iou: float
    max_track_age_seconds: float
    security_rules_enabled: bool = True
    security_normal_start_hour: int = 6
    security_normal_end_hour: int = 22
    crowding_person_threshold: int = 4
    loiter_seconds: float = 15.0
    security_event_cooldown_seconds: float = 10.0
    security_high_risk_cooldown_seconds: float = 5.0
    security_location: str = "KUET Main Gate"
    security_save_event_snapshot: bool = True
    demo_profile: str = "gate_daytime"
    # Gate-zone ROI filtering (normalized 0.0–1.0 frame fractions)
    gate_zone_enabled: bool = True
    gate_zone_x1: float = 0.15
    gate_zone_y1: float = 0.20
    gate_zone_x2: float = 0.85
    gate_zone_y2: float = 1.00
    # Tracker missed-frames pruning
    max_track_missed_frames: int = 10


def ensure_project_dirs(config: Settings) -> None:
    for path in (
        config.cache_dir,
        config.cache_dir / "pip",
        config.cache_dir / "pycache",
        config.cache_dir / "torch",
        config.cache_dir / "ultralytics",
        config.cache_dir / "matplotlib",
        config.model_dir,
        config.runs_dir,
        config.benchmark_output_dir,
        config.tracking_output_dir,
        config.video_output_dir,
        config.data_dir,
        config.snapshot_dir,
        config.evidence_dir,
        config.sample_video_dir,
        config.database_path.parent,
    ):
        path.mkdir(parents=True, exist_ok=True)

    os.environ["PIP_CACHE_DIR"] = str(config.cache_dir / "pip")
    os.environ["PYTHONPYCACHEPREFIX"] = str(config.cache_dir / "pycache")
    os.environ["ULTRALYTICS_CONFIG_DIR"] = str(config.cache_dir / "ultralytics")
    os.environ["YOLO_CONFIG_DIR"] = str(config.cache_dir / "ultralytics")
    os.environ["TORCH_HOME"] = str(config.cache_dir / "torch")
    os.environ["XDG_CACHE_HOME"] = str(config.cache_dir)
    os.environ["MPLCONFIGDIR"] = str(config.cache_dir / "matplotlib")
    os.environ["YOLO_VERBOSE"] = "False"


def get_runtime_info() -> dict[str, Any]:
    try:
        import cv2

        opencv_version = cv2.__version__
    except Exception:
        opencv_version = None

    torch_available = False
    torch_version = None
    cuda_available = False
    cuda_version = None
    cuda_device_count = 0
    cuda_device_name = None
    try:
        import torch

        torch_available = True
        torch_version = getattr(torch, "__version__", None)
        cuda_available = bool(torch.cuda.is_available())
        cuda_version = getattr(torch.version, "cuda", None)
        cuda_device_count = int(torch.cuda.device_count()) if cuda_available else 0
        if cuda_available and cuda_device_count:
            cuda_device_name = torch.cuda.get_device_name(0)
    except Exception:
        pass

    try:
        import ultralytics  # noqa: F401

        ultralytics_available = True
    except Exception:
        ultralytics_available = False

    return {
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "torch_available": torch_available,
        "torch_version": torch_version,
        "cuda_available": cuda_available,
        "cuda_version": cuda_version,
        "cuda_device_count": cuda_device_count,
        "cuda_device_name": cuda_device_name,
        "ultralytics_available": ultralytics_available,
        "opencv_version": opencv_version,
    }


def load_settings() -> Settings:
    cache_dir = _project_path(os.getenv("CACHE_DIR", ".cache"))
    model_dir = _project_path(os.getenv("MODEL_DIR", "models"))
    runs_dir = _project_path(os.getenv("RUNS_DIR", "runs"))
    benchmark_output_dir = _project_path(
        os.getenv("BENCHMARK_OUTPUT_DIR", "runs/benchmarks")
    )
    tracking_output_dir = _project_path(
        os.getenv("TRACKING_OUTPUT_DIR", "runs/tracking")
    )
    data_dir = _project_path(os.getenv("DATA_DIR", "data"))
    snapshot_dir = _project_path(os.getenv("SNAPSHOT_DIR", "snapshots"))
    evidence_dir = _project_path(os.getenv("EVIDENCE_DIR", "snapshots/evidence"))
    sample_video_dir = _project_path(os.getenv("SAMPLE_VIDEO_DIR", "sample_videos"))
    video_output_dir = _project_path(os.getenv("VIDEO_OUTPUT_DIR", "runs/videos"))
    database_path = _project_path(os.getenv("DATABASE_PATH", "smartkuet.db"))

    config = Settings(
        app_name=os.getenv("APP_NAME", "SmartKUET Sentinel"),
        location=os.getenv("LOCATION", "KUET Main Gate"),
        camera_source=_camera_source(os.getenv("CAMERA_SOURCE", "0")),
        database_path=database_path,
        cache_dir=cache_dir,
        model_dir=model_dir,
        runs_dir=runs_dir,
        benchmark_output_dir=benchmark_output_dir,
        tracking_output_dir=tracking_output_dir,
        data_dir=data_dir,
        snapshot_dir=snapshot_dir,
        evidence_dir=evidence_dir,
        sample_video_dir=sample_video_dir,
        video_output_dir=video_output_dir,
        camera_reconnect_seconds=float(os.getenv("CAMERA_RECONNECT_SECONDS", "2")),
        camera_loop_video=_bool(os.getenv("CAMERA_LOOP_VIDEO", "true")),
        yolo_enabled=_bool(os.getenv("YOLO_ENABLED", "true")),
        yolo_model_path=_project_path(os.getenv("YOLO_MODEL_PATH", "models/yolov8n.pt")),
        yolo_conf=float(os.getenv("YOLO_CONF", "0.35")),
        yolo_imgsz=int(os.getenv("YOLO_IMGSZ", "640")),
        yolo_device=os.getenv("YOLO_DEVICE", "auto"),
        detection_every_n_frames=max(1, int(os.getenv("DETECTION_EVERY_N_FRAMES", "3"))),
        tracking_enabled=_bool(os.getenv("TRACKING_ENABLED", "true")),
        tracker_type=os.getenv("TRACKER_TYPE", "bytetrack"),
        track_person_class_name=os.getenv("TRACK_PERSON_CLASS_NAME", "person"),
        track_conf=float(os.getenv("TRACK_CONF", "0.35")),
        track_iou=float(os.getenv("TRACK_IOU", "0.5")),
        max_track_age_seconds=float(os.getenv("MAX_TRACK_AGE_SECONDS", "5")),
        security_rules_enabled=_bool(os.getenv("SECURITY_RULES_ENABLED", "true")),
        security_normal_start_hour=int(os.getenv("SECURITY_NORMAL_START_HOUR", "6")),
        security_normal_end_hour=int(os.getenv("SECURITY_NORMAL_END_HOUR", "22")),
        crowding_person_threshold=int(os.getenv("CROWDING_PERSON_THRESHOLD", "4")),
        loiter_seconds=float(os.getenv("LOITER_SECONDS", "15")),
        security_event_cooldown_seconds=float(
            os.getenv("SECURITY_EVENT_COOLDOWN_SECONDS", "10")
        ),
        security_high_risk_cooldown_seconds=float(
            os.getenv("SECURITY_HIGH_RISK_COOLDOWN_SECONDS", "5")
        ),
        security_location=os.getenv(
            "SECURITY_LOCATION",
            os.getenv("LOCATION", "KUET Main Gate"),
        ),
        security_save_event_snapshot=_bool(
            os.getenv("SECURITY_SAVE_EVENT_SNAPSHOT", "true")
        ),
        demo_profile=os.getenv("DEMO_PROFILE", "gate_daytime"),
        gate_zone_enabled=_bool(os.getenv("GATE_ZONE_ENABLED", "true")),
        gate_zone_x1=float(os.getenv("GATE_ZONE_X1", "0.15")),
        gate_zone_y1=float(os.getenv("GATE_ZONE_Y1", "0.20")),
        gate_zone_x2=float(os.getenv("GATE_ZONE_X2", "0.85")),
        gate_zone_y2=float(os.getenv("GATE_ZONE_Y2", "1.00")),
        max_track_missed_frames=max(1, int(os.getenv("MAX_TRACK_MISSED_FRAMES", "10"))),
    )
    ensure_project_dirs(config)
    return config


settings = load_settings()
