import sqlite3

from core.database import Database


def test_init_db_creates_tables(tmp_path):
    database = Database(tmp_path / "smartkuet.db")
    database.init_db()

    with sqlite3.connect(database.path) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

    assert {"persons", "security_incidents", "exam_events"}.issubset(tables)


def test_create_and_list_security_incident(tmp_path):
    database = Database(tmp_path / "smartkuet.db")
    database.init_db()

    incident_id = database.create_security_incident(
        location="KUET Main Gate",
        detected_name="Unknown outsider",
        status_color="red",
        confidence=0.84,
        instruction="Deny entry and notify supervisor.",
    )
    incidents = database.list_security_incidents()

    assert incident_id == 1
    assert len(incidents) == 1
    assert incidents[0]["location"] == "KUET Main Gate"
    assert incidents[0]["status_color"] == "red"


def test_create_and_list_exam_event(tmp_path):
    database = Database(tmp_path / "smartkuet.db")
    database.init_db()

    event_id = database.create_exam_event(
        seat_no="B-07",
        behavior_type="Frequent side glance",
        score_added=1.5,
        current_score=1.5,
        color_level="yellow",
    )
    events = database.list_exam_events()

    assert event_id == 1
    assert len(events) == 1
    assert events[0]["seat_no"] == "B-07"
    assert events[0]["color_level"] == "yellow"
