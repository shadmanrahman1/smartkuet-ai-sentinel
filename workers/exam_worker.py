import asyncio
from datetime import datetime, timezone
from itertools import cycle
from typing import AsyncIterator

from core.schemas import ExamEvent


EXAM_EVENTS = (
    {
        "seat_no": "A-12",
        "behavior_type": "Normal posture",
        "score_added": 0.0,
        "color_level": "green",
    },
    {
        "seat_no": "B-07",
        "behavior_type": "Frequent side glance",
        "score_added": 1.5,
        "color_level": "yellow",
    },
    {
        "seat_no": "C-19",
        "behavior_type": "Repeated desk movement",
        "score_added": 3.0,
        "color_level": "orange",
    },
    {
        "seat_no": "D-03",
        "behavior_type": "High attention behavior",
        "score_added": 5.0,
        "color_level": "red",
    },
)


async def mock_exam_events(interval: float = 2.0) -> AsyncIterator[ExamEvent]:
    current_score = 0.0
    for event in cycle(EXAM_EVENTS):
        current_score = max(0.0, min(10.0, current_score + event["score_added"]))
        if event["color_level"] == "green":
            current_score = 0.0

        yield {
            "module": "exam",
            "seat_no": event["seat_no"],
            "behavior_type": event["behavior_type"],
            "score_added": event["score_added"],
            "current_score": current_score,
            "color_level": event["color_level"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await asyncio.sleep(interval)
