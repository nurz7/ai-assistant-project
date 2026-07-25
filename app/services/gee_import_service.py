import csv
from pathlib import Path

from pydantic import ValidationError

from app.models.schemas import GEEObservationInput

MAX_IMPORT_BYTES = 5 * 1024 * 1024
SAFE_COLUMNS = (
    "reservoir_name",
    "observation_date",
    "source",
    "scl_water_area_km2",
    "mndwi_area_km2",
    "ndwi_area_km2",
    "cloud_percent",
    "roi_area_km2",
    "method_version",
)
SENSITIVE_COLUMNS = {
    "object_id",
    "dam_id",
    "reservoir_id",
    "xmin",
    "ymin",
    "xmax",
    "ymax",
    "latitude",
    "longitude",
    "normal_level",
    "dead_level",
    "level_m",
    "volume_m3",
}


class GEEImportError(ValueError):
    """Raised when a sanitized GEE CSV cannot be imported."""


class UnsafeGEEImportError(GEEImportError):
    """Raised when an import contains fields excluded from the public MVP."""


def load_sanitized_gee_csv(path: Path) -> list[GEEObservationInput]:
    if not path.exists() or not path.is_file():
        raise GEEImportError(f"CSV file does not exist: {path}")
    if path.stat().st_size > MAX_IMPORT_BYTES:
        raise GEEImportError("CSV file exceeds the 5 MB demo import limit")

    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        headers = tuple(reader.fieldnames or ())
        _validate_headers(headers)

        records: list[GEEObservationInput] = []
        for row_number, row in enumerate(reader, start=2):
            try:
                records.append(GEEObservationInput.model_validate(row))
            except ValidationError as error:
                raise GEEImportError(
                    f"Invalid sanitized GEE row at line {row_number}: {error}"
                ) from error

    if not records:
        raise GEEImportError("CSV file contains no observation rows")
    return records


def _validate_headers(headers: tuple[str, ...]) -> None:
    header_set = set(headers)
    sensitive = sorted(header_set & SENSITIVE_COLUMNS)
    if sensitive:
        raise UnsafeGEEImportError(
            "CSV contains fields excluded from the public MVP: "
            f"{', '.join(sensitive)}"
        )

    missing = sorted(set(SAFE_COLUMNS) - header_set)
    extra = sorted(header_set - set(SAFE_COLUMNS))
    if missing or extra:
        details: list[str] = []
        if missing:
            details.append(f"missing: {', '.join(missing)}")
        if extra:
            details.append(f"unsupported: {', '.join(extra)}")
        raise GEEImportError("Invalid sanitized GEE columns; " + "; ".join(details))

    if headers != SAFE_COLUMNS:
        raise GEEImportError("Sanitized GEE columns must use the documented order")
