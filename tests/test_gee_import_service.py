import tempfile
import unittest
from pathlib import Path

from app.services.gee_import_service import (
    GEEImportError,
    UnsafeGEEImportError,
    load_sanitized_gee_csv,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class GEEImportServiceTests(unittest.TestCase):
    def test_loads_committed_synthetic_sample(self) -> None:
        records = load_sanitized_gee_csv(
            PROJECT_ROOT / "data" / "samples" / "synthetic_gee_observations.csv"
        )

        self.assertEqual(len(records), 3)
        self.assertEqual(records[0].reservoir_name, "Tasmola Demo")
        self.assertEqual(records[-1].cloud_percent, 54.0)

    def test_rejects_sensitive_identifier_column(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "unsafe.csv"
            path.write_text(
                "dam_id,reservoir_name,observation_date,source,"
                "scl_water_area_km2,mndwi_area_km2,ndwi_area_km2,"
                "cloud_percent,roi_area_km2,method_version\n"
                "219,Demo,2025-05-01,Sentinel-2,1,1,1,5,2,v1\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(UnsafeGEEImportError, "dam_id"):
                load_sanitized_gee_csv(path)

    def test_rejects_water_area_larger_than_roi(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "invalid.csv"
            path.write_text(
                "reservoir_name,observation_date,source,scl_water_area_km2,"
                "mndwi_area_km2,ndwi_area_km2,cloud_percent,roi_area_km2,"
                "method_version\n"
                "Demo,2025-05-01,Sentinel-2,3,3,3,5,2,v1\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(GEEImportError, "Water area"):
                load_sanitized_gee_csv(path)
