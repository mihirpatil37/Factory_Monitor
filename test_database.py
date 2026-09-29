import sqlite3
import pytest
import database


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """Run every test against a throwaway database file, never the real factory.db."""
    monkeypatch.chdir(tmp_path)
    yield


def test_init_db_creates_table():
    database.init_db()
    conn = sqlite3.connect("factory.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='sensor_readings'"
    )
    assert cursor.fetchone() is not None
    conn.close()


def test_save_reading_stores_row():
    database.init_db()
    database.save_reading("factory/line1/machine1/temperature", "72.5")

    conn = sqlite3.connect("factory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT topic, value FROM sensor_readings")
    row = cursor.fetchone()
    conn.close()

    assert row == ("factory/line1/machine1/temperature", "72.5")


def test_get_latest_readings_returns_most_recent_first():
    database.init_db()
    database.save_reading("factory/line1/machine1/temperature", "70.0")
    database.save_reading("factory/line1/machine1/temperature", "75.0")

    rows = database.get_latest_readings()

    assert rows[0][1] == "75.0"  # most recently inserted row comes first
    assert len(rows) == 2


def test_get_latest_readings_caps_at_ten():
    database.init_db()
    for i in range(15):
        database.save_reading("factory/line1/machine1/temperature", str(i))

    rows = database.get_latest_readings()

    assert len(rows) == 10  # boundary: the query's LIMIT 10 is enforced
