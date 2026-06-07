from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import cv2
import numpy as np


DEFAULT_ALLOWED_CLASSES = {
    "person",
    "cell phone",
    "backpack",
    "handbag",
    "car",
    "motorcycle",
    "bicycle",
    "bus",
    "truck",
}

VEHICLE_CLASSES = {"car", "motorcycle", "bicycle", "bus", "truck"}


class YOLODetector:
    def __init__(
        self,
        model_path: str | Path,
        conf: float = 0.35,
        imgsz: int = 640,
        device: str = "auto",
        allowed_classes: Iterable[str] | None = None,
    ):
        self.model_path = Path(model_path)
        self.conf = conf
        self.imgsz = imgsz
        self.requested_device = device
        self.error: str | None = None
        self.selected_device = self._select_device(device)
        self.allowed_classes = set(allowed_classes or DEFAULT_ALLOWED_CLASSES)
        self._model: Any | None = None

    def _load_model(self) -> Any:
        if self._model is None:
            try:
                from ultralytics import YOLO

                self.model_path.parent.mkdir(parents=True, exist_ok=True)
                self._model = YOLO(str(self.model_path))
                self.error = None
            except Exception as exc:
                self.error = str(exc)
                raise
        return self._model

    @staticmethod
    def _cuda_available() -> bool:
        try:
            import torch

            return bool(torch.cuda.is_available())
        except Exception:
            return False

    def _select_device(self, device: str) -> str:
        requested = (device or "auto").strip().lower()
        if requested == "auto":
            return "cuda" if self._cuda_available() else "cpu"

        if requested.startswith("cuda") and not self._cuda_available():
            self.error = "CUDA requested but unavailable; falling back to CPU"
            return "cpu"

        return requested

    @staticmethod
    def _class_name(names: Any, class_id: int) -> str:
        if isinstance(names, dict):
            return str(names.get(class_id, class_id))
        if isinstance(names, list) and class_id < len(names):
            return str(names[class_id])
        return str(class_id)

    def _predict(self, frame: np.ndarray, device: str | None) -> Any:
        model = self._load_model()
        kwargs: dict[str, Any] = {
            "source": frame,
            "conf": self.conf,
            "imgsz": self.imgsz,
            "verbose": False,
        }
        if device and device != "auto":
            kwargs["device"] = device
        return model.predict(**kwargs)

    def detect(self, frame: np.ndarray) -> list[dict[str, Any]]:
        try:
            results = self._predict(frame, self.selected_device)
            self.error = None
        except Exception as exc:
            self.error = str(exc)
            if self.selected_device == "cpu":
                raise
            self.selected_device = "cpu"
            results = self._predict(frame, "cpu")

        detections: list[dict[str, Any]] = []
        for result in results:
            boxes = getattr(result, "boxes", None)
            if boxes is None:
                continue

            names = getattr(result, "names", getattr(self._model, "names", {}))
            for box in boxes:
                class_id = int(box.cls[0].item())
                class_name = self._class_name(names, class_id)
                if class_name not in self.allowed_classes:
                    continue

                detections.append(
                    {
                        "class_id": class_id,
                        "class_name": class_name,
                        "confidence": float(box.conf[0].item()),
                        "bbox": [float(value) for value in box.xyxy[0].tolist()],
                    }
                )
        return detections

    def get_status(self) -> dict[str, Any]:
        return {
            "loaded": self._model is not None,
            "model_path": str(self.model_path),
            "requested_device": self.requested_device,
            "selected_device": self.selected_device,
            "conf": self.conf,
            "imgsz": self.imgsz,
            "error": self.error,
        }

    @staticmethod
    def filter_by_class(
        detections: list[dict[str, Any]],
        class_name: str,
    ) -> list[dict[str, Any]]:
        return [
            detection
            for detection in detections
            if detection.get("class_name") == class_name
        ]

    def annotate(
        self,
        frame: np.ndarray,
        detections: list[dict[str, Any]],
    ) -> np.ndarray:
        annotated = frame.copy()
        for detection in detections:
            x1, y1, x2, y2 = [int(value) for value in detection["bbox"]]
            class_name = detection["class_name"]
            color = self._color_for_class(class_name)
            label = f"{class_name} {detection['confidence']:.2f}"

            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            label_y = max(y1 - 8, 18)
            cv2.putText(
                annotated,
                label,
                (x1, label_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                color,
                2,
                cv2.LINE_AA,
            )
        return annotated

    @staticmethod
    def _color_for_class(class_name: str) -> tuple[int, int, int]:
        if class_name == "person":
            return (72, 187, 120)
        if class_name == "cell phone":
            return (38, 38, 220)
        if class_name in VEHICLE_CLASSES:
            return (235, 165, 52)
        return (29, 162, 234)

    @staticmethod
    def summarize(detections: list[dict[str, Any]]) -> dict[str, Any]:
        class_counts = Counter(str(item["class_name"]) for item in detections)
        return {
            "total": len(detections),
            "person_count": class_counts.get("person", 0),
            "phone_count": class_counts.get("cell phone", 0),
            "vehicle_count": sum(class_counts.get(name, 0) for name in VEHICLE_CLASSES),
            "classes": dict(sorted(class_counts.items())),
        }
