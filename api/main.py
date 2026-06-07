import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncIterator

import cv2
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from core.camera import CameraStream
from core.config import ensure_project_dirs, get_runtime_info, settings
from core.database import Database
from core.detector import YOLODetector
from core.security_rules import SecurityRulesEngine, select_highest_security_event
from core.tracker import PersonTracker
from core.video_processor import VideoProcessor
from workers.exam_worker import mock_exam_events
from workers.security_worker import mock_security_events


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = PROJECT_ROOT / "dashboard"

db = Database(settings.database_path)
camera: CameraStream | None = None
video_processor: VideoProcessor | None = None
security_rules_engine: SecurityRulesEngine | None = None


def build_security_rules_engine() -> SecurityRulesEngine:
    return SecurityRulesEngine(
        rules_enabled=settings.security_rules_enabled,
        normal_start_hour=settings.security_normal_start_hour,
        normal_end_hour=settings.security_normal_end_hour,
        crowding_person_threshold=settings.crowding_person_threshold,
        loiter_seconds=settings.loiter_seconds,
        event_cooldown_seconds=settings.security_event_cooldown_seconds,
        high_risk_cooldown_seconds=settings.security_high_risk_cooldown_seconds,
        location=settings.security_location,
    )


def create_security_incident_from_event(
    event: dict,
    snapshot_path: str | None,
) -> None:
    db.create_security_incident(
        location=event.get("location") or settings.security_location,
        detected_name=event.get("event_type") or "Track-based event",
        status_color=event.get("level") or "yellow",
        confidence=event.get("confidence"),
        snapshot_path=snapshot_path,
        instruction=event.get("instruction"),
        guard_action=None,
        created_at=event.get("timestamp"),
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    global camera, video_processor, security_rules_engine
    ensure_project_dirs(settings)
    db.init_db()
    security_rules_engine = build_security_rules_engine()
    camera = CameraStream(
        settings.camera_source,
        reconnect_seconds=settings.camera_reconnect_seconds,
        loop_video=settings.camera_loop_video,
    )

    if settings.yolo_enabled:
        detector = YOLODetector(
            model_path=settings.yolo_model_path,
            conf=settings.yolo_conf,
            imgsz=settings.yolo_imgsz,
            device=settings.yolo_device,
        )
        tracker = None
        if settings.tracking_enabled:
            tracker = PersonTracker(
                tracker_type=settings.tracker_type,
                max_age_seconds=settings.max_track_age_seconds,
                iou_threshold=settings.track_iou,
                person_class_name=settings.track_person_class_name,
                min_confidence=settings.track_conf,
            )
        video_processor = VideoProcessor(
            camera=camera,
            detector=detector,
            tracker=tracker,
            detection_every_n_frames=settings.detection_every_n_frames,
            enabled=True,
            tracking_enabled=settings.tracking_enabled,
            security_rules_engine=security_rules_engine,
            security_incident_writer=create_security_incident_from_event,
            evidence_dir=settings.evidence_dir,
            save_security_event_snapshot=settings.security_save_event_snapshot,
            project_root=PROJECT_ROOT,
        )

    yield
    if video_processor is not None:
        video_processor.release()
        video_processor = None
    if camera is not None:
        camera.release()
        camera = None
    security_rules_engine = None


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.mount("/dashboard", StaticFiles(directory=DASHBOARD_DIR), name="dashboard")


def dashboard_file(name: str) -> FileResponse:
    return FileResponse(DASHBOARD_DIR / name)


def camera_status() -> dict:
    if camera is None:
        return {
            "source": str(settings.camera_source),
            "source_type": "unknown",
            "is_opened": False,
            "frame_count": 0,
            "width": None,
            "height": None,
            "fps_estimate": None,
            "last_error": "Camera not initialized",
        }
    return camera.get_status()


def detection_summary() -> dict:
    if not settings.yolo_enabled:
        return {
            "enabled": False,
            "total": 0,
            "person_count": 0,
            "phone_count": 0,
            "vehicle_count": 0,
            "classes": {},
            "error": "YOLO disabled",
        }

    if video_processor is None:
        return {
            "enabled": True,
            "total": 0,
            "person_count": 0,
            "phone_count": 0,
            "vehicle_count": 0,
            "classes": {},
            "error": "Video processor unavailable",
        }

    return video_processor.get_latest_summary()


def video_status() -> dict:
    if not settings.yolo_enabled:
        return {
            "yolo_enabled": False,
            "model_path": str(settings.yolo_model_path),
            "device": settings.yolo_device,
            "selected_device": None,
            "processed_frames": 0,
            "last_inference_ms": None,
            "avg_inference_ms": None,
            "effective_fps": None,
            "model_error": "YOLO disabled",
            "latest_summary": detection_summary(),
            "tracking_enabled": False,
            "tracker_type": None,
            "active_track_count": 0,
            "total_tracks_seen": 0,
            "active_tracks": [],
        }

    if video_processor is None:
        return {
            "yolo_enabled": True,
            "model_path": str(settings.yolo_model_path),
            "device": settings.yolo_device,
            "selected_device": None,
            "processed_frames": 0,
            "last_inference_ms": None,
            "avg_inference_ms": None,
            "effective_fps": None,
            "model_error": "Video processor unavailable",
            "latest_summary": detection_summary(),
            "tracking_enabled": settings.tracking_enabled,
            "tracker_type": None,
            "active_track_count": 0,
            "total_tracks_seen": 0,
            "active_tracks": [],
        }

    return video_processor.get_status()


def tracking_summary() -> dict:
    if not settings.tracking_enabled:
        return {
            "enabled": False,
            "tracker_type": None,
            "active_track_count": 0,
            "total_tracks_seen": 0,
            "active_tracks": [],
            "error": "Tracking disabled",
        }

    if video_processor is None:
        return {
            "enabled": True,
            "tracker_type": settings.tracker_type,
            "active_track_count": 0,
            "total_tracks_seen": 0,
            "active_tracks": [],
            "error": "Video processor unavailable",
        }

    return video_processor.get_tracking_summary()


def security_status_from_events(
    engine: SecurityRulesEngine,
    events: list[dict],
) -> dict:
    event = select_highest_security_event(events)
    if event is None:
        latest_level = "green"
        latest_event_type = "NORMAL_ACTIVITY"
        latest_instruction = "Monitor normally."
        last_event_at = None
    else:
        latest_level = event.get("level", "green")
        latest_event_type = event.get("event_type", "NORMAL_ACTIVITY")
        latest_instruction = event.get("instruction", "Monitor normally.")
        last_event_at = event.get("timestamp")

    return {
        "rules_enabled": engine.rules_enabled,
        "latest_events": events,
        "latest_level": latest_level,
        "latest_event_type": latest_event_type,
        "latest_instruction": latest_instruction,
        "last_event_at": last_event_at,
        "last_evaluated_at": datetime.now(timezone.utc).isoformat(),
        "cooldowns": engine.get_cooldowns(),
        **engine.get_config(),
    }


def security_status() -> dict:
    if video_processor is not None:
        return video_processor.get_security_status()

    if security_rules_engine is None:
        return {
            "rules_enabled": False,
            "latest_events": [],
            "latest_level": "green",
            "latest_event_type": "NORMAL_ACTIVITY",
            "latest_instruction": "Security rules unavailable.",
            "last_event_at": None,
            "last_evaluated_at": None,
            "cooldowns": {},
            "normal_start_hour": settings.security_normal_start_hour,
            "normal_end_hour": settings.security_normal_end_hour,
            "crowding_person_threshold": settings.crowding_person_threshold,
            "loiter_seconds": settings.loiter_seconds,
            "event_cooldown_seconds": settings.security_event_cooldown_seconds,
            "high_risk_cooldown_seconds": settings.security_high_risk_cooldown_seconds,
            "location": settings.security_location,
        }

    security_rules_engine.evaluate(
        tracking_summary=tracking_summary(),
        detection_summary=detection_summary(),
        camera_status=camera_status(),
    )
    return security_status_from_events(
        security_rules_engine,
        security_rules_engine.get_current_events(),
    )


def normal_security_event() -> dict:
    timestamp = datetime.now(timezone.utc).isoformat()
    tracking = tracking_summary()
    detections = detection_summary()
    tracks = tracking.get("active_tracks") or []
    return {
        "event_type": "NORMAL_ACTIVITY",
        "level": "green",
        "title": "Normal activity",
        "instruction": "Monitor normally.",
        "confidence": 0.7,
        "location": settings.security_location,
        "related_track_ids": [
            track.get("track_id")
            for track in tracks
            if track.get("track_id") is not None
        ],
        "evidence": {
            "active_track_count": tracking.get("active_track_count", len(tracks)),
            "max_track_age_seconds": max(
                [float(track.get("age_seconds", 0.0)) for track in tracks] or [0.0]
            ),
            "person_count": detections.get("person_count", 0),
            "phone_count": detections.get("phone_count", 0),
            "vehicle_count": detections.get("vehicle_count", 0),
        },
        "timestamp": timestamp,
    }


def error_frame(message: str = "Camera unavailable") -> bytes:
    frame = VideoProcessor.fallback_frame()
    ok, encoded = cv2.imencode(".jpg", frame)
    if not ok:
        return b""
    return encoded.tobytes()


async def mjpeg_frames() -> AsyncIterator[bytes]:
    fallback = error_frame()
    while True:
        try:
            if settings.yolo_enabled and video_processor is not None:
                jpeg = video_processor.get_annotated_jpeg()
            else:
                jpeg = camera.encode_jpeg() if camera is not None else None
        except Exception:
            jpeg = None

        payload = jpeg or fallback
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n"
            b"Cache-Control: no-store\r\n\r\n"
            + payload
            + b"\r\n"
        )
        await asyncio.sleep(0.1)


@app.get("/")
async def index():
    return dashboard_file("index.html")


@app.get("/guard")
async def guard():
    return dashboard_file("guard.html")


@app.get("/exam")
async def exam():
    return dashboard_file("exam.html")


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}


@app.get("/api/persons")
async def list_persons():
    return db.list_persons()


@app.get("/api/security/incidents")
async def list_security_incidents():
    return db.list_security_incidents()


@app.get("/api/exam/events")
async def list_exam_events():
    return db.list_exam_events()


@app.get("/api/runtime/status")
async def runtime_status():
    return {
        "app": settings.app_name,
        "runtime": get_runtime_info(),
        "camera": camera_status(),
        "video_processor": video_status(),
        "detections": detection_summary(),
        "tracking": tracking_summary(),
        "security_status": security_status(),
    }


@app.get("/api/camera/status")
async def api_camera_status():
    return camera_status()


@app.get("/api/video/status")
async def api_video_status():
    return video_status()


@app.get("/api/detections/latest")
async def latest_detections():
    return detection_summary()


@app.get("/api/tracking/latest")
async def latest_tracking():
    return tracking_summary()


@app.post("/api/tracking/reset")
async def reset_tracking():
    if video_processor is not None:
        video_processor.reset_tracker()
    return {
        "reset": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/security/status")
async def api_security_status():
    return security_status()


@app.post("/api/security/rules/reset")
async def reset_security_rules():
    if video_processor is not None:
        video_processor.reset_security_rules()
    elif security_rules_engine is not None:
        security_rules_engine.reset_cooldowns()
    return {
        "reset": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "security_status": security_status(),
    }


@app.post("/api/evidence/snapshot")
async def save_evidence_snapshot():
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    path = settings.evidence_dir / f"snapshot_{timestamp}.jpg"

    if video_processor is not None:
        saved = video_processor.save_latest_annotated_frame(path)
    else:
        frame = camera.latest_frame if camera is not None else None
        saved = bool(frame is not None and cv2.imwrite(str(path), frame))

    if not saved:
        return {
            "saved": False,
            "path": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": "No live frame available to save",
        }

    try:
        display_path = str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        display_path = str(path)

    return {
        "saved": True,
        "path": display_path,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/video_feed")
async def video_feed():
    return StreamingResponse(
        mjpeg_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


def websocket_security_payload(event: dict, status: dict) -> dict:
    level = event.get("level", "green")
    return {
        "module": "security",
        "source": "rules_engine",
        "event_type": event.get("event_type", "NORMAL_ACTIVITY"),
        "level": level,
        "status_color": level,
        "detected_name": event.get("event_type", "NORMAL_ACTIVITY"),
        "title": event.get("title", "Normal activity"),
        "instruction": event.get("instruction", "Monitor normally."),
        "confidence": event.get("confidence", 0.7),
        "location": event.get("location", settings.security_location),
        "related_track_ids": event.get("related_track_ids", []),
        "evidence": event.get("evidence", {}),
        "timestamp": event.get("timestamp", datetime.now(timezone.utc).isoformat()),
        "detection_summary": detection_summary(),
        "tracking_summary": tracking_summary(),
        "security_status": status,
    }


@app.websocket("/ws/security")
async def websocket_security(websocket: WebSocket):
    await websocket.accept()
    try:
        if security_rules_engine is None or not security_rules_engine.rules_enabled:
            async for event in mock_security_events(settings.location, interval=2.0):
                event["detection_summary"] = detection_summary()
                event["tracking_summary"] = tracking_summary()
                db.create_security_incident(
                    location=event["location"],
                    detected_name=event["detected_name"],
                    status_color=event["status_color"],
                    confidence=event["confidence"],
                    instruction=event["instruction"],
                )
                await websocket.send_json(event)
            return

        while True:
            status = security_status()
            event = select_highest_security_event(status.get("latest_events", []))
            if event is None:
                event = normal_security_event()
            await websocket.send_json(websocket_security_payload(event, status))
            await asyncio.sleep(2.0)
    except WebSocketDisconnect:
        return


@app.websocket("/ws/exam")
async def websocket_exam(websocket: WebSocket):
    await websocket.accept()
    try:
        async for event in mock_exam_events(interval=2.0):
            db.create_exam_event(
                seat_no=event["seat_no"],
                behavior_type=event["behavior_type"],
                score_added=event["score_added"],
                current_score=event["current_score"],
                color_level=event["color_level"],
            )
            await websocket.send_json(event)
    except WebSocketDisconnect:
        return


@app.exception_handler(FileNotFoundError)
async def not_found_handler(_, exc: FileNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})
