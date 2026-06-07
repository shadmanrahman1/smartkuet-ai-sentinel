from typing import TypedDict


class SecurityEvent(TypedDict):
    module: str
    location: str
    detected_name: str
    status_color: str
    confidence: float
    instruction: str
    timestamp: str


class ExamEvent(TypedDict):
    module: str
    seat_no: str
    behavior_type: str
    score_added: float
    current_score: float
    color_level: str
    timestamp: str
