from core.config import Settings, ensure_project_dirs


def test_ensure_project_dirs_creates_local_paths(tmp_path):
    settings = Settings(
        app_name="SmartKUET Sentinel",
        location="KUET Main Gate",
        camera_source=0,
        database_path=tmp_path / "smartkuet.db",
        cache_dir=tmp_path / ".cache",
        model_dir=tmp_path / "models",
        runs_dir=tmp_path / "runs",
        benchmark_output_dir=tmp_path / "runs" / "benchmarks",
        tracking_output_dir=tmp_path / "runs" / "tracking",
        data_dir=tmp_path / "data",
        snapshot_dir=tmp_path / "snapshots",
        evidence_dir=tmp_path / "snapshots" / "evidence",
        sample_video_dir=tmp_path / "sample_videos",
        video_output_dir=tmp_path / "runs" / "videos",
        camera_reconnect_seconds=2.0,
        camera_loop_video=True,
        yolo_enabled=True,
        yolo_model_path=tmp_path / "models" / "yolov8n.pt",
        yolo_conf=0.35,
        yolo_imgsz=640,
        yolo_device="auto",
        detection_every_n_frames=3,
        tracking_enabled=True,
        tracker_type="bytetrack",
        track_person_class_name="person",
        track_conf=0.35,
        track_iou=0.5,
        max_track_age_seconds=5.0,
    )

    ensure_project_dirs(settings)

    assert settings.model_dir.is_dir()
    assert settings.runs_dir.is_dir()
    assert settings.benchmark_output_dir.is_dir()
    assert settings.tracking_output_dir.is_dir()
    assert settings.video_output_dir.is_dir()
    assert settings.data_dir.is_dir()
    assert settings.snapshot_dir.is_dir()
    assert settings.evidence_dir.is_dir()
    assert settings.sample_video_dir.is_dir()
    assert (settings.cache_dir / "torch").is_dir()
    assert (settings.cache_dir / "ultralytics").is_dir()
