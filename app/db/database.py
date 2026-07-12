import sqlite3
from pathlib import Path

from app.core.config import settings
from app.db.seed_data import seed_database

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS reservoirs (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    region TEXT NOT NULL,
    passport_area_km2 REAL NOT NULL,
    normal_level_m REAL,
    dead_level_m REAL,
    latitude REAL,
    longitude REAL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS satellite_observations (
    id INTEGER PRIMARY KEY,
    reservoir_id INTEGER NOT NULL,
    observation_date TEXT NOT NULL,
    source TEXT NOT NULL,
    scl_water_area_km2 REAL NOT NULL,
    mndwi_area_km2 REAL NOT NULL,
    ndwi_area_km2 REAL NOT NULL,
    cloud_percent REAL NOT NULL,
    roi_area_km2 REAL NOT NULL,
    method_version TEXT NOT NULL,
    FOREIGN KEY (reservoir_id) REFERENCES reservoirs(id)
);

CREATE TABLE IF NOT EXISTS area_level_reference (
    id INTEGER PRIMARY KEY,
    reservoir_id INTEGER NOT NULL,
    area_km2 REAL NOT NULL,
    level_m REAL NOT NULL,
    volume_m3 REAL NOT NULL,
    source TEXT NOT NULL,
    reliability_note TEXT NOT NULL,
    FOREIGN KEY (reservoir_id) REFERENCES reservoirs(id)
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY,
    reservoir_id INTEGER NOT NULL,
    observation_id INTEGER,
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (reservoir_id) REFERENCES reservoirs(id),
    FOREIGN KEY (observation_id) REFERENCES satellite_observations(id)
);
"""


def resolve_db_path(db_path: Path | None = None) -> Path:
    return db_path or settings.reservoir_db_path


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    path = resolve_db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(db_path: Path | None = None) -> Path:
    path = resolve_db_path(db_path)
    with get_connection(path) as connection:
        connection.executescript(SCHEMA_SQL)
        seed_database(connection)
    return path


def ensure_database(db_path: Path | None = None) -> Path:
    path = resolve_db_path(db_path)
    if not path.exists():
        return initialize_database(path)

    with get_connection(path) as connection:
        connection.executescript(SCHEMA_SQL)
        seed_database(connection)
    return path
