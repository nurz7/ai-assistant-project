import sqlite3

RESERVOIRS = [
    (
        1,
        "Tasmola",
        "Akmola Region",
        4.20,
        352.4,
        346.1,
        50.1234,
        71.4567,
        "Synthetic demo record for portfolio testing; not an official registry value.",
    ),
    (
        2,
        "Koksu Demo Reservoir",
        "Jetisu Region",
        2.75,
        611.8,
        606.2,
        44.8120,
        78.2150,
        "Synthetic demo record with stable flood-period observations.",
    ),
    (
        3,
        "Sarybulak Demo Reservoir",
        "Karaganda Region",
        1.80,
        428.5,
        423.0,
        48.5220,
        73.1010,
        "Synthetic demo record used for small-reservoir anomaly examples.",
    ),
]

SATELLITE_OBSERVATIONS = [
    (1, 1, "2025-05-03", "Sentinel-2 L2A", 3.82, 3.94, 3.75, 8.5, 5.10, "demo-v0.1"),
    (2, 1, "2025-05-13", "Sentinel-2 L2A", 4.05, 4.18, 3.95, 12.0, 5.10, "demo-v0.1"),
    (3, 1, "2025-05-23", "Sentinel-2 L2A", 2.10, 3.65, 2.25, 54.0, 5.10, "demo-v0.1"),
    (4, 1, "2025-06-02", "Sentinel-2 L2A", 4.85, 4.95, 4.70, 6.0, 5.10, "demo-v0.1"),
    (5, 2, "2025-05-04", "Sentinel-2 L2A", 2.41, 2.48, 2.36, 7.0, 3.20, "demo-v0.1"),
    (6, 2, "2025-05-14", "Sentinel-2 L2A", 2.63, 2.66, 2.58, 9.5, 3.20, "demo-v0.1"),
    (7, 2, "2025-05-24", "Sentinel-2 L2A", 2.71, 2.69, 2.62, 11.0, 3.20, "demo-v0.1"),
    (8, 3, "2025-05-06", "Sentinel-2 L2A", 1.28, 1.35, 1.22, 15.0, 2.40, "demo-v0.1"),
    (9, 3, "2025-05-16", "Sentinel-2 L2A", 1.05, 1.62, 1.10, 38.0, 2.40, "demo-v0.1"),
]

AREA_LEVEL_REFERENCE = [
    (
        1,
        1,
        3.50,
        349.8,
        780_000.0,
        "Synthetic demo area-level table",
        "Demonstration only; not validated for exact operational water levels.",
    ),
    (
        2,
        1,
        4.20,
        352.4,
        1_050_000.0,
        "Synthetic demo area-level table",
        "Demonstration only; not validated for exact operational water levels.",
    ),
    (
        3,
        2,
        2.75,
        611.8,
        520_000.0,
        "Synthetic demo area-level table",
        "Demonstration only; not validated for exact operational water levels.",
    ),
    (
        4,
        3,
        1.80,
        428.5,
        310_000.0,
        "Synthetic demo area-level table",
        "Demonstration only; not validated for exact operational water levels.",
    ),
]

ALERTS = [
    (
        1,
        1,
        3,
        "high_cloud",
        "high",
        "Cloud percentage is high, so the water mask should be reviewed manually.",
        "2025-05-23T10:30:00Z",
    ),
    (
        2,
        3,
        9,
        "method_conflict",
        "medium",
        "NDWI, MNDWI, and SCL water area estimates diverge in this observation.",
        "2025-05-16T10:30:00Z",
    ),
]


def seed_database(connection: sqlite3.Connection) -> None:
    existing_count = connection.execute("SELECT COUNT(*) FROM reservoirs").fetchone()[0]
    if existing_count:
        return

    connection.executemany(
        """
        INSERT INTO reservoirs (
            id, name, region, passport_area_km2, normal_level_m, dead_level_m,
            latitude, longitude, notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        RESERVOIRS,
    )
    connection.executemany(
        """
        INSERT INTO satellite_observations (
            id, reservoir_id, observation_date, source, scl_water_area_km2,
            mndwi_area_km2, ndwi_area_km2, cloud_percent, roi_area_km2,
            method_version
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        SATELLITE_OBSERVATIONS,
    )
    connection.executemany(
        """
        INSERT INTO area_level_reference (
            id, reservoir_id, area_km2, level_m, volume_m3, source,
            reliability_note
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        AREA_LEVEL_REFERENCE,
    )
    connection.executemany(
        """
        INSERT INTO alerts (
            id, reservoir_id, observation_id, alert_type, severity, message,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ALERTS,
    )
