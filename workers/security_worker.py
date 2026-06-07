import asyncio
from datetime import datetime, timezone
from itertools import cycle
from typing import AsyncIterator

from core.schemas import SecurityEvent


SECURITY_EVENTS = (
    {
        "detected_name": "Known KUETian",
        "status_color": "green",
        "confidence": 0.96,
        "instruction": "Allow normal campus entry.",
    },
    {
        "detected_name": "Uncertain identity",
        "status_color": "yellow",
        "confidence": 0.62,
        "instruction": "Verify ID before allowing entry.",
    },
    {
        "detected_name": "Unknown outsider",
        "status_color": "red",
        "confidence": 0.84,
        "instruction": "Deny entry and notify supervisor.",
    },
)


async def mock_security_events(
    location: str,
    interval: float = 2.0,
) -> AsyncIterator[SecurityEvent]:
    for event in cycle(SECURITY_EVENTS):
        yield {
            "module": "security",
            "location": location,
            "detected_name": event["detected_name"],
            "status_color": event["status_color"],
            "confidence": event["confidence"],
            "instruction": event["instruction"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await asyncio.sleep(interval)
