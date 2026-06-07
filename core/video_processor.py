import time
from datetime import datetime, timezone
from pathlib import Path
from threading import Event, Lock, Thread
from typing import Any

import cv2
import numpy as np

from core.camera import CameraStream
from core.detector import YOLODetector
from core.tracker import PersonTracker


class VideoProcessor:
    def __init__(
        self,
        camera: CameraStream,
        detector: YOLODetector | None,
        tracker: PersonTracker | None = None,
        detection_every_n_frames: int = 3,
        enabled: bool = True,
        tracking_enabled: bool = True,
    ):
        self.camera = camera
        self.detector = detector
        self.tracker = tracker
        self.detection_every_n_frames = max(1, detection_every_n_frames)
        self.enabled = enabled
        self.tracking_enabled = tracking_enabled and tracker is not None
        self.processed_frames = 0
        self.last_inference_ms: float | None = None
        self.avg_inference_ms: float | None = None
        self.effective_fps: float | None = None
        self.model_error: str | None = None
        self.last_detection_at: str | None = None
        self.selected_device = detector.selected_device if detector else None
        self.model_path = str(detector.model_path) if detector else None
        self.requested_device = detector.requested_device if detector else None
        self._latest_raw_frame: np.ndarray | None = None
        self._latest_annotated_frame: np.ndarray | None = None
        self._latest_detections: list[dict[str, Any]] = []
        self._active_tracks: list[dict[str, Any]] = []
        self._latest_summary = self._empty_summary(error="Waiting for camera frame")
        self._latest_tracking_summary = self._empty_tracking_summary(
            enabled=self.tracking_enabled,
            tracker_type=self.tracker.backend if self.tracker is not None else None,
        )
        self._frame_index = 0
        self._inference_samples: list[float] = []
        self._first_inference_at: float | None = None
        self._lock = Lock()
        self._stop = Event()
        self._thread = Thread(target=self._loop, daemon=True)
        self._thread.start()

    @staticmethod
    def _empty_summary(error: str | None = None, enabled: bool = True) -> dict[str, Any]:
        return {
            "enabled": enabled,
            "total": 0,
            "person_count": 0,
            "phone_count": 0,
            "vehicle_count": 0,
            "classes": {},
            "error": error,
        }

    @staticmethod
    def _empty_tracking_summary(
        enabled: bool = False,
        tracker_type: str | None = None,
        error: str | None = None,
    ) -> dict[str, Any]:
        return {
            "enabled": enabled,
            "tracker_type": tracker_type,
            "active_track_count": 0,
            "total_tracks_seen": 0,
            "active_tracks": [],
            "error": error,
        }

    @staticmethod
    def fallback_frame() -> np.ndarray:
        frame = np.zeros((480, 854, 3), dtype=np.uint8)
        frame[:, :] = (8, 17, 31)
        lines = [
            ("SmartKUET Sentinel", 42, 1.1, (226, 232, 240)),
            ("Camera unavailable", 108, 0.9, (248, 113, 113)),
            ("Set CAMERA_SOURCE=sample_videos/demo.mp4 or phone IP URL", 166, 0.65, (148, 163, 184)),
        ]
        for text, y, scale, color in lines:
            cv2.putText(
                frame,
                text,
                (38, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                scale,
                color,
                2,
                cv2.LINE_AA,
            )
        return frame

    @staticmethod
    def _overlay_warning(frame: np.ndarray, message: str) -> np.ndarray:
        annotated = frame.copy()
        cv2.rectangle(annotated, (0, 0), (annotated.shape[1], 48), (38, 38, 38), -1)
        cv2.putText(
            annotated,
            message,
            (16, 32),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        return annotated

    @staticmethod
    def _encode_jpeg(frame: np.ndarray) -> bytes | None:
        ok, encoded = cv2.imencode(".jpg", frame)
        if not ok:
            return None
        return encoded.tobytes()

    def _record_inference(self, elapsed_ms: float) -> None:
        self.processed_frames += 1
        self.last_inference_ms = elapsed_ms
        self._inference_samples.append(elapsed_ms)
        self._inference_samples = self._inference_samples[-60:]
        self.avg_inference_ms = sum(self._inference_samples) / len(self._inference_samples)
        if self._first_inference_at is None:
            self._first_inference_at = time.perf_counter()
        elapsed_seconds = max(0.001, time.perf_counter() - self._first_inference_at)
        self.effective_fps = self.processed_frames / elapsed_seconds
        self.last_detection_at = datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _track_color(track_id: int) -> tuple[int, int, int]:
        palette = [
            (52, 211, 153),
            (56, 189, 248),
            (251, 191, 36),
            (248, 113, 113),
            (167, 139, 250),
        ]
        return palette[(track_id - 1) % len(palette)]

    def _annotate_with_tracking(
        self,
        frame: np.ndarray,
        detections: list[dict[str, Any]],
        active_tracks: list[dict[str, Any]],
    ) -> np.ndarray:
        if self.detector is None:
            return frame.copy()

        non_person_detections = [
            detection
            for detection in detections
            if detection.get("class_name") != "person"
        ]
        annotated = self.detector.annotate(frame, non_person_detections)

        for track in active_tracks:
            x1, y1, x2, y2 = [int(value) for value in track["bbox"]]
            track_id = int(track["track_id"])
            color = self._track_color(track_id)
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

    def _update_tracking(
        self,
        frame: np.ndarray,
        detections: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if not self.tracking_enabled or self.tracker is None:
            return self._empty_tracking_summary(
                enabled=False,
                error="Tracking disabled",
            )

        try:
            updated_tracks = self.tracker.update(frame, detections)
            status = self.tracker.get_status()
            return {
                "enabled": True,
                "tracker_type": status["tracker_type"],
                "requested_tracker_type": status["requested_tracker_type"],
                "active_track_count": status["active_track_count"],
                "total_tracks_seen": status["total_tracks_seen"],
                "active_tracks": status["active_tracks"],
                "updated_tracks": updated_tracks,
                "error": status.get("last_error"),
            }
        except Exception as exc:
            return self._empty_tracking_summary(
                enabled=True,
                tracker_type="unavailable",
                error=str(exc),
            )

    def _loop(self) -> None:
        while not self._stop.is_set():
            frame = self.camera.latest_frame
            if frame is None:
                with self._lock:
                    self._latest_summary = self._empty_summary(error="Waiting for camera frame")
                time.sleep(0.05)
                continue

            with self._lock:
                self._latest_raw_frame = frame.copy()

            if not self.enabled or self.detector is None:
                with self._lock:
                    self._latest_annotated_frame = frame.copy()
                    self._latest_summary = self._empty_summary(
                        enabled=False,
                        error="YOLO disabled",
                    )
                time.sleep(0.03)
                continue

            self._frame_index += 1
            should_detect = self._frame_index % self.detection_every_n_frames == 0

            try:
                if should_detect:
                    start = time.perf_counter()
                    self._latest_detections = self.detector.detect(frame)
                    elapsed_ms = (time.perf_counter() - start) * 1000
                    self._record_inference(elapsed_ms)
                    tracking_summary = self._update_tracking(
                        frame,
                        self._latest_detections,
                    )
                    self._active_tracks = tracking_summary.get("active_tracks", [])
                    self._latest_tracking_summary = tracking_summary

                summary = self.detector.summarize(self._latest_detections)
                summary.update({"enabled": True, "error": None})
                if self.tracking_enabled:
                    annotated = self._annotate_with_tracking(
                        frame,
                        self._latest_detections,
                        self._active_tracks,
                    )
                else:
                    annotated = self.detector.annotate(frame, self._latest_detections)
                self.model_error = self.detector.error
                self.selected_device = self.detector.selected_device
            except Exception as exc:
                self.model_error = f"YOLO unavailable: {exc}"
                summary = self._empty_summary(error=self.model_error)
                self._latest_tracking_summary = self._empty_tracking_summary(
                    enabled=self.tracking_enabled,
                    tracker_type="unavailable",
                    error=self.model_error,
                )
                annotated = self._overlay_warning(frame, "YOLO unavailable")

            with self._lock:
                self._latest_annotated_frame = annotated
                self._latest_summary = summary

            time.sleep(0.03)

    def get_annotated_jpeg(self) -> bytes | None:
        with self._lock:
            frame = (
                self._latest_annotated_frame.copy()
                if self._latest_annotated_frame is not None
                else None
            )
        if frame is None:
            frame = self.fallback_frame()
        return self._encode_jpeg(frame)

    def get_latest_annotated_frame(self) -> np.ndarray | None:
        with self._lock:
            if self._latest_annotated_frame is None:
                return None
            return self._latest_annotated_frame.copy()

    def save_latest_annotated_frame(self, path: str | Path) -> bool:
        frame = self.get_latest_annotated_frame()
        if frame is None:
            return False
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        return bool(cv2.imwrite(str(path), frame))

    def get_latest_summary(self) -> dict[str, Any]:
        with self._lock:
            return dict(self._latest_summary)

    def get_tracking_summary(self) -> dict[str, Any]:
        with self._lock:
            summary = dict(self._latest_tracking_summary)
            summary["active_tracks"] = [
                dict(track)
                for track in self._latest_tracking_summary.get("active_tracks", [])
            ]
            return summary

    def reset_tracker(self) -> None:
        if self.tracker is not None:
            self.tracker.reset()
        with self._lock:
            self._active_tracks = []
            self._latest_tracking_summary = self._empty_tracking_summary(
                enabled=self.tracking_enabled,
                tracker_type=self.tracker.backend if self.tracker is not None else None,
            )

    def get_status(self) -> dict[str, Any]:
        latest_summary = self.get_latest_summary()
        tracking_summary = self.get_tracking_summary()
        detector_status = self.detector.get_status() if self.detector else None
        return {
            "yolo_enabled": self.enabled,
            "model_path": self.model_path,
            "device": self.requested_device,
            "selected_device": self.selected_device,
            "processed_frames": self.processed_frames,
            "last_inference_ms": round(self.last_inference_ms, 2)
            if self.last_inference_ms is not None
            else None,
            "avg_inference_ms": round(self.avg_inference_ms, 2)
            if self.avg_inference_ms is not None
            else None,
            "effective_fps": round(self.effective_fps, 2)
            if self.effective_fps is not None
            else None,
            "model_error": self.model_error,
            "last_detection_at": self.last_detection_at,
            "latest_summary": latest_summary,
            "tracking_enabled": self.tracking_enabled,
            "tracker_type": tracking_summary.get("tracker_type"),
            "active_track_count": tracking_summary.get("active_track_count", 0),
            "total_tracks_seen": tracking_summary.get("total_tracks_seen", 0),
            "active_tracks": tracking_summary.get("active_tracks", []),
            "latest_tracking_summary": tracking_summary,
            "detector": detector_status,
        }

    def release(self) -> None:
        self._stop.set()
        if self._thread.is_alive():
            self._thread.join(timeout=2.0)
