"""
core/object_cue_detection.py — Milestone 2C

Local-only object-cue detection service scaffold (ID cards, lanyards, visitor badges, bags, helmets).
No cloud calls, no model download.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ObjectCueStatus:
    DISABLED = "DISABLED"
    MODEL_NOT_CONFIGURED = "MODEL_NOT_CONFIGURED"
    READY = "READY"


class ObjectCueDetectionService:
    """
    Local object-cue detection service.
    Acts as a supporting signal provider for security risk fusion.
    """

    def __init__(
        self,
        enabled: bool = False,
        model_path: Optional[Path] = None,
        supported_cues: Optional[list[str]] = None,
    ):
        self.enabled = enabled
        self.model_path = Path(model_path) if model_path else None
        self.supported_cues = supported_cues or ["id_card", "lanyard", "visitor_badge", "bag", "helmet"]
        
        self._model_loaded = False
        if self.enabled and self.model_path:
            self._check_model_exists()

    def _check_model_exists(self) -> bool:
        if self.model_path and self.model_path.exists() and self.model_path.is_file():
            self._model_loaded = True
            return True
        self._model_loaded = False
        return False

    def get_status(self) -> dict:
        """Return structured status metadata."""
        if not self.enabled:
            status = ObjectCueStatus.DISABLED
            instruction = "Object cue detection is disabled. Enable in config/env."
            configured = False
        elif not self._check_model_exists():
            status = ObjectCueStatus.MODEL_NOT_CONFIGURED
            instruction = f"Local model file missing or not configured at: {self.model_path}. Run checklist checks."
            configured = False
        else:
            status = ObjectCueStatus.READY
            instruction = "Object cue detection ready for local offline inference."
            configured = True

        return {
            "enabled": self.enabled,
            "configured": configured,
            "model_path": str(self.model_path) if self.model_path else None,
            "status": status,
            "supported_cues": self.supported_cues,
            "instruction": instruction,
        }
