import tempfile
import unittest
from pathlib import Path

from app.services.report_service import build_monitoring_report


class ReportServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "reservoir_demo.sqlite"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_build_report_combines_data_anomalies_and_sources(self) -> None:
        report = build_monitoring_report(
            "Tasmola",
            start_date="2025-05-01",
            end_date="2025-05-31",
            db_path=self.db_path,
        )

        self.assertIsNotNone(report)
        if report is None:
            self.fail("Expected a monitoring report")
        self.assertEqual(report.reservoir.name, "Tasmola")
        self.assertEqual(len(report.observations), 3)
        self.assertGreaterEqual(len(report.anomaly_flags), 2)
        self.assertIsNotNone(report.calculation_result)
        self.assertGreaterEqual(len(report.sources), 3)
        self.assertEqual(report.quality_assessment.status, "USE_WITH_CAUTION")
        self.assertIn("# Monitoring Report: Tasmola", report.text)
        self.assertIn("## Automatic Quality Control", report.text)
        self.assertIn("## Method Notes", report.text)
        self.assertIn("cloud 54.0%", report.text)
        self.assertIn("do not establish an exact water level", report.text)
        self.assertIn(report.sources[0].chunk_id, report.text)

    def test_build_report_returns_none_without_matching_observations(self) -> None:
        report = build_monitoring_report(
            "Tasmola",
            start_date="2024-01-01",
            end_date="2024-01-31",
            db_path=self.db_path,
        )

        self.assertIsNone(report)

    def test_build_report_returns_none_for_unknown_reservoir(self) -> None:
        report = build_monitoring_report("Unknown", db_path=self.db_path)

        self.assertIsNone(report)
