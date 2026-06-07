import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Database:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def init_db(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS persons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    kuet_id TEXT,
                    role TEXT,
                    department TEXT,
                    hall TEXT,
                    face_embedding BLOB,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS security_incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    location TEXT NOT NULL,
                    detected_name TEXT,
                    status_color TEXT NOT NULL,
                    confidence REAL,
                    snapshot_path TEXT,
                    instruction TEXT,
                    guard_action TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS exam_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    seat_no TEXT,
                    behavior_type TEXT NOT NULL,
                    score_added REAL,
                    current_score REAL,
                    color_level TEXT NOT NULL,
                    snapshot_path TEXT,
                    examiner_action TEXT,
                    created_at TEXT NOT NULL
                );
                """
            )

    @staticmethod
    def _rows(cursor: sqlite3.Cursor) -> list[dict[str, Any]]:
        return [dict(row) for row in cursor.fetchall()]

    def create_person(
        self,
        name: str,
        kuet_id: str | None = None,
        role: str | None = None,
        department: str | None = None,
        hall: str | None = None,
        face_embedding: bytes | None = None,
    ) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO persons (
                    name, kuet_id, role, department, hall, face_embedding, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (name, kuet_id, role, department, hall, face_embedding, utc_now()),
            )
            return int(cursor.lastrowid)

    def list_persons(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            cursor = connection.execute("SELECT * FROM persons ORDER BY id DESC")
            return self._rows(cursor)

    def create_security_incident(
        self,
        location: str,
        status_color: str,
        detected_name: str | None = None,
        confidence: float | None = None,
        snapshot_path: str | None = None,
        instruction: str | None = None,
        guard_action: str | None = None,
        created_at: str | None = None,
    ) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO security_incidents (
                    location, detected_name, status_color, confidence, snapshot_path,
                    instruction, guard_action, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    location,
                    detected_name,
                    status_color,
                    confidence,
                    snapshot_path,
                    instruction,
                    guard_action,
                    created_at or utc_now(),
                ),
            )
            return int(cursor.lastrowid)

    def list_security_incidents(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as connection:
            cursor = connection.execute(
                "SELECT * FROM security_incidents ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            return self._rows(cursor)

    def create_exam_event(
        self,
        behavior_type: str,
        color_level: str,
        seat_no: str | None = None,
        score_added: float | None = None,
        current_score: float | None = None,
        snapshot_path: str | None = None,
        examiner_action: str | None = None,
    ) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO exam_events (
                    seat_no, behavior_type, score_added, current_score, color_level,
                    snapshot_path, examiner_action, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    seat_no,
                    behavior_type,
                    score_added,
                    current_score,
                    color_level,
                    snapshot_path,
                    examiner_action,
                    utc_now(),
                ),
            )
            return int(cursor.lastrowid)

    def list_exam_events(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as connection:
            cursor = connection.execute(
                "SELECT * FROM exam_events ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            return self._rows(cursor)
