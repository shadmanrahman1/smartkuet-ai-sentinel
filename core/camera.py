import time
from pathlib import Path
from threading import Event, Lock, Thread
from typing import Any, Union

import cv2
import numpy as np


VIDEO_SUFFIXES = {".mp4", ".avi", ".mov", ".mkv", ".m4v", ".webm"}


def normalize_camera_source(source: Union[int, str]) -> Union[int, str]:
    if isinstance(source, str) and source.strip().isdigit():
        return int(source)
    return source


def classify_camera_source(source: Union[int, str]) -> str:
    value = normalize_camera_source(source)
    if isinstance(value, int):
        return "webcam"

    text = str(value).strip().lower()
    if text.startswith("rtsp://"):
        return "rtsp"
    if text.startswith("http://") or text.startswith("https://"):
        return "ip_camera"
    if Path(text).suffix.lower() in VIDEO_SUFFIXES:
        return "video_file"
    return "unknown"


class CameraStream:
    def __init__(
        self,
        source: Union[int, str] = 0,
        reconnect_seconds: float = 2.0,
        loop_video: bool = True,
    ):
        self.source = normalize_camera_source(source)
        self.source_type = classify_camera_source(source)
        self.reconnect_seconds = max(0.2, reconnect_seconds)
        self.loop_video = loop_video
        self.capture: cv2.VideoCapture | None = None
        self.last_error: str | None = None
        self.frame_count = 0
        self.width: int | None = None
        self.height: int | None = None
        self.fps_estimate: float | None = None
        self._latest_frame: np.ndarray | None = None
        self._last_frame_time: float | None = None
        self._fps_samples: list[float] = []
        self._lock = Lock()
        self._stop = Event()
        self._thread = Thread(target=self._read_frames, daemon=True)
        self._thread.start()

    @property
    def is_opened(self) -> bool:
        return bool(self.capture and self.capture.isOpened())

    @property
    def latest_frame(self) -> np.ndarray | None:
        with self._lock:
            if self._latest_frame is None:
                return None
            return self._latest_frame.copy()

    def _open_capture(self) -> None:
        self._release_capture()
        capture = cv2.VideoCapture(self.source)
        if not capture.isOpened():
            self.last_error = f"Unable to open camera source: {self.source}"
            capture.release()
            return

        self.capture = capture
        self.last_error = None
        self.width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)) or None
        self.height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)) or None

    def _release_capture(self) -> None:
        if self.capture is not None:
            self.capture.release()
        self.capture = None

    def _record_frame_stats(self, frame: np.ndarray) -> None:
        now = time.perf_counter()
        if self._last_frame_time is not None:
            delta = now - self._last_frame_time
            if delta > 0:
                self._fps_samples.append(1.0 / delta)
                self._fps_samples = self._fps_samples[-30:]
                self.fps_estimate = sum(self._fps_samples) / len(self._fps_samples)
        self._last_frame_time = now

        self.frame_count += 1
        self.height, self.width = frame.shape[:2]

    def _handle_read_failure(self) -> None:
        if self.source_type == "video_file" and self.loop_video and self.capture is not None:
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.last_error = None
            return

        self.last_error = f"Failed to read frame from source: {self.source}"
        self._release_capture()
        time.sleep(self.reconnect_seconds)

    def _read_frames(self) -> None:
        next_open_attempt = 0.0
        while not self._stop.is_set():
            if not self.is_opened:
                now = time.monotonic()
                if now >= next_open_attempt:
                    self._open_capture()
                    next_open_attempt = now + self.reconnect_seconds
                time.sleep(0.05)
                continue

            assert self.capture is not None
            ok, frame = self.capture.read()
            if not ok:
                self._handle_read_failure()
                continue

            with self._lock:
                self._latest_frame = frame
                self._record_frame_stats(frame)

    def get_status(self) -> dict[str, Any]:
        with self._lock:
            return {
                "source": str(self.source),
                "source_type": self.source_type,
                "is_opened": self.is_opened,
                "frame_count": self.frame_count,
                "width": self.width,
                "height": self.height,
                "fps_estimate": round(self.fps_estimate, 2)
                if self.fps_estimate is not None
                else None,
                "last_error": self.last_error,
            }

    def encode_jpeg(self) -> bytes | None:
        frame = self.latest_frame
        if frame is None:
            return None

        ok, encoded = cv2.imencode(".jpg", frame)
        if not ok:
            return None
        return encoded.tobytes()

    def release(self) -> None:
        self._stop.set()
        if self._thread.is_alive():
            self._thread.join(timeout=1.5)
        self._release_capture()
