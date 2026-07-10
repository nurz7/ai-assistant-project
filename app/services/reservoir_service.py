from pathlib import Path

from app.db.database import ensure_database, get_connection
from app.models.schemas import (
    AnomalyFlag,
    CalculationResult,
    ReservoirObservation,
    ReservoirReference,
)

HIGH_CLOUD_THRESHOLD = 40.0
MODERATE_CLOUD_THRESHOLD = 30.0
PASSPORT_AREA_WARNING_PERCENT = 15.0
PASSPORT_AREA_HIGH_PERCENT = 30.0
METHOD_CONFLICT_PERCENT = 20.0

AREA_METHOD_COLUMNS = {
    "scl": "scl_water_area_km2",
    "mndwi": "mndwi_area_km2",
    "ndwi": "ndwi_area_km2",
}


def _normalize_name(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _reservoir_from_row(row) -> ReservoirReference:
    return ReservoirReference(
        name=row["name"],
        region=row["region"],
        passport_area_km2=row["passport_area_km2"],
        normal_level_m=row["normal_level_m"],
        dead_level_m=row["dead_level_m"],
        latitude=row["latitude"],
        longitude=row["longitude"],
        notes=row["notes"],
    )


def _observation_from_row(row) -> ReservoirObservation:
    return ReservoirObservation(
        observation_id=row["id"],
        observation_date=row["observation_date"],
        source=row["source"],
        scl_water_area_km2=row["scl_water_area_km2"],
        mndwi_area_km2=row["mndwi_area_km2"],
        ndwi_area_km2=row["ndwi_area_km2"],
        cloud_percent=row["cloud_percent"],
        roi_area_km2=row["roi_area_km2"],
        method_version=row["method_version"],
    )


def _find_reservoir_row(connection, name: str):
    normalized_name = _normalize_name(name)
    return connection.execute(
        """
        SELECT *
        FROM reservoirs
        WHERE lower(name) = ?
           OR lower(name) LIKE ?
           OR ? LIKE '%' || lower(name) || '%'
        ORDER BY length(name)
        LIMIT 1
        """,
        (normalized_name, f"%{normalized_name}%", normalized_name),
    ).fetchone()


def list_reservoir_names(*, db_path: Path | None = None) -> list[str]:
    ensure_database(db_path)
    with get_connection(db_path) as connection:
        rows = connection.execute("SELECT name FROM reservoirs ORDER BY name").fetchall()
    return [row["name"] for row in rows]


def extract_reservoir_name(text: str, *, db_path: Path | None = None) -> str | None:
    normalized_text = _normalize_name(text)
    for name in list_reservoir_names(db_path=db_path):
        normalized_name = _normalize_name(name)
        first_token = normalized_name.split()[0]
        if normalized_name in normalized_text or first_token in normalized_text:
            return name
    return None


def get_reservoir_summary(
    name: str,
    *,
    db_path: Path | None = None,
) -> ReservoirReference | None:
    ensure_database(db_path)
    with get_connection(db_path) as connection:
        row = _find_reservoir_row(connection, name)
        return _reservoir_from_row(row) if row else None


def get_observations(
    name: str,
    *,
    start_date: str | None = None,
    end_date: str | None = None,
    db_path: Path | None = None,
) -> list[ReservoirObservation]:
    ensure_database(db_path)
    with get_connection(db_path) as connection:
        reservoir_row = _find_reservoir_row(connection, name)
        if not reservoir_row:
            return []

        filters = ["reservoir_id = ?"]
        parameters: list[str | int] = [reservoir_row["id"]]
        if start_date:
            filters.append("observation_date >= ?")
            parameters.append(start_date)
        if end_date:
            filters.append("observation_date <= ?")
            parameters.append(end_date)

        rows = connection.execute(
            f"""
            SELECT *
            FROM satellite_observations
            WHERE {' AND '.join(filters)}
            ORDER BY observation_date
            """,
            parameters,
        ).fetchall()

    return [_observation_from_row(row) for row in rows]


def compare_area_to_passport(
    name: str,
    *,
    method: str = "mndwi",
    observation_date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    db_path: Path | None = None,
) -> CalculationResult | None:
    method_key = method.strip().lower()
    if method_key not in AREA_METHOD_COLUMNS:
        raise ValueError(f"Unsupported area method: {method}")

    ensure_database(db_path)
    with get_connection(db_path) as connection:
        reservoir_row = _find_reservoir_row(connection, name)
        if not reservoir_row:
            return None

        query = """
            SELECT *
            FROM satellite_observations
            WHERE reservoir_id = ?
        """
        parameters: list[str | int] = [reservoir_row["id"]]
        if observation_date:
            query += " AND observation_date = ?"
            parameters.append(observation_date)
        if start_date:
            query += " AND observation_date >= ?"
            parameters.append(start_date)
        if end_date:
            query += " AND observation_date <= ?"
            parameters.append(end_date)
        query += " ORDER BY observation_date DESC LIMIT 1"

        observation_row = connection.execute(query, parameters).fetchone()
        if not observation_row:
            return None

    passport_area = float(reservoir_row["passport_area_km2"])
    observed_area = float(observation_row[AREA_METHOD_COLUMNS[method_key]])
    difference = observed_area - passport_area
    percent_difference = (difference / passport_area) * 100
    direction = "higher than" if difference > 0 else "lower than"

    return CalculationResult(
        metric=f"{method_key}_area_vs_passport_area_percent_difference",
        value=round(percent_difference, 2),
        unit="%",
        explanation=(
            f"On {observation_row['observation_date']}, {method_key.upper()} "
            f"satellite-derived water area was {observed_area:.2f} km2 versus "
            f"passport area {passport_area:.2f} km2, which is "
            f"{abs(difference):.2f} km2 {direction} the passport area."
        ),
    )


def find_area_anomalies(
    name: str,
    *,
    start_date: str | None = None,
    end_date: str | None = None,
    db_path: Path | None = None,
) -> list[AnomalyFlag]:
    reservoir = get_reservoir_summary(name, db_path=db_path)
    if not reservoir or reservoir.passport_area_km2 is None:
        return []

    observations = get_observations(
        name,
        start_date=start_date,
        end_date=end_date,
        db_path=db_path,
    )
    flags: list[AnomalyFlag] = []
    for observation in observations:
        flags.extend(_cloud_flags(observation))
        flags.extend(_passport_area_flags(observation, reservoir.passport_area_km2))
        flags.extend(_method_conflict_flags(observation))
    return flags


def _cloud_flags(observation: ReservoirObservation) -> list[AnomalyFlag]:
    if observation.cloud_percent >= HIGH_CLOUD_THRESHOLD:
        severity = "high"
    elif observation.cloud_percent >= MODERATE_CLOUD_THRESHOLD:
        severity = "medium"
    else:
        return []

    return [
        AnomalyFlag(
            observation_id=observation.observation_id,
            observation_date=observation.observation_date,
            alert_type="high_cloud",
            severity=severity,
            message=(
                f"Cloud cover is {observation.cloud_percent:.1f}%, so the "
                "water mask should be reviewed before operational use."
            ),
        )
    ]


def _passport_area_flags(
    observation: ReservoirObservation,
    passport_area_km2: float,
) -> list[AnomalyFlag]:
    percent_difference = (
        (observation.mndwi_area_km2 - passport_area_km2) / passport_area_km2
    ) * 100
    absolute_percent = abs(percent_difference)
    if absolute_percent < PASSPORT_AREA_WARNING_PERCENT:
        return []

    direction = "above" if percent_difference > 0 else "below"
    severity = "high" if absolute_percent >= PASSPORT_AREA_HIGH_PERCENT else "medium"
    return [
        AnomalyFlag(
            observation_id=observation.observation_id,
            observation_date=observation.observation_date,
            alert_type="passport_area_deviation",
            severity=severity,
            message=(
                f"MNDWI area is {absolute_percent:.1f}% {direction} passport "
                "area. This is an anomaly flag, not a water-level conclusion."
            ),
        )
    ]


def _method_conflict_flags(observation: ReservoirObservation) -> list[AnomalyFlag]:
    areas = [
        observation.scl_water_area_km2,
        observation.mndwi_area_km2,
        observation.ndwi_area_km2,
    ]
    mean_area = sum(areas) / len(areas)
    if mean_area == 0:
        return []

    spread_percent = ((max(areas) - min(areas)) / mean_area) * 100
    if spread_percent < METHOD_CONFLICT_PERCENT:
        return []

    return [
        AnomalyFlag(
            observation_id=observation.observation_id,
            observation_date=observation.observation_date,
            alert_type="method_conflict",
            severity="medium",
            message=(
                "SCL, MNDWI, and NDWI water area estimates differ by "
                f"{spread_percent:.1f}% of their mean area."
            ),
        )
    ]
