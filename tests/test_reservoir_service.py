import tempfile
import unittest
from pathlib import Path

from app.services.reservoir_service import (
    compare_area_to_passport,
    extract_reservoir_name,
    find_area_anomalies,
    get_observations,
    get_reservoir_summary,
)


class ReservoirServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "reservoir_demo.sqlite"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_get_reservoir_summary_returns_synthetic_profile(self) -> None:
        summary = get_reservoir_summary("Tasmola", db_path=self.db_path)

        self.assertIsNotNone(summary)
        assert summary is not None
        self.assertEqual(summary.name, "Tasmola")
        self.assertEqual(summary.region, "Akmola Region")
        self.assertEqual(summary.passport_area_km2, 4.20)
        self.assertIn("Synthetic demo record", summary.notes)

    def test_get_observations_filters_by_period(self) -> None:
        observations = get_observations(
            "Tasmola",
            start_date="2025-05-01",
            end_date="2025-05-31",
            db_path=self.db_path,
        )

        self.assertEqual(len(observations), 3)
        self.assertEqual(observations[0].observation_date, "2025-05-03")
        self.assertEqual(observations[-1].observation_date, "2025-05-23")

    def test_compare_area_to_passport_uses_latest_observation_in_period(self) -> None:
        result = compare_area_to_passport(
            "Tasmola",
            start_date="2025-05-01",
            end_date="2025-05-31",
            db_path=self.db_path,
        )

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(
            result.metric,
            "mndwi_area_vs_passport_area_percent_difference",
        )
        self.assertEqual(result.value, -13.1)
        self.assertIn("2025-05-23", result.explanation)

    def test_find_area_anomalies_flags_cloud_and_method_conflict(self) -> None:
        flags = find_area_anomalies(
            "Tasmola",
            start_date="2025-05-01",
            end_date="2025-05-31",
            db_path=self.db_path,
        )

        flag_types = {flag.alert_type for flag in flags}
        self.assertIn("high_cloud", flag_types)
        self.assertIn("method_conflict", flag_types)

    def test_extract_reservoir_name_matches_demo_name_in_text(self) -> None:
        name = extract_reservoir_name(
            "Compare latest Tasmola MNDWI area to passport area.",
            db_path=self.db_path,
        )

        self.assertEqual(name, "Tasmola")

    def test_unknown_reservoir_returns_empty_results(self) -> None:
        self.assertIsNone(get_reservoir_summary("Unknown", db_path=self.db_path))
        self.assertEqual(get_observations("Unknown", db_path=self.db_path), [])
        self.assertIsNone(compare_area_to_passport("Unknown", db_path=self.db_path))
