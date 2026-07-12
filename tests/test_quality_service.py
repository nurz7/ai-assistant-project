import tempfile
import unittest
from pathlib import Path

from app.models.schemas import ReservoirObservation
from app.services.quality_service import (
    assess_observation_quality,
    assess_reservoir_quality,
)


def _observation(
    observation_id: int,
    *,
    scl: float,
    mndwi: float,
    ndwi: float,
    cloud: float = 5.0,
) -> ReservoirObservation:
    return ReservoirObservation(
        observation_id=observation_id,
        observation_date=f"2025-05-{observation_id:02d}",
        source="Sentinel-2 L2A",
        scl_water_area_km2=scl,
        mndwi_area_km2=mndwi,
        ndwi_area_km2=ndwi,
        cloud_percent=cloud,
        roi_area_km2=10.0,
        method_version="test-v1",
    )


class QualityServiceTests(unittest.TestCase):
    def test_tasmola_may_is_use_with_caution(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            assessment = assess_reservoir_quality(
                "Tasmola",
                start_date="2025-05-01",
                end_date="2025-05-31",
                db_path=Path(temp_dir) / "demo.sqlite",
            )

        self.assertIsNotNone(assessment)
        if assessment is None:
            self.fail("Expected a quality assessment")
        self.assertEqual(assessment.status, "USE_WITH_CAUTION")
        self.assertEqual(assessment.dates_count, 3)
        self.assertEqual(assessment.high_cloud_share, 0.3333)
        self.assertEqual(assessment.method_conflict_share, 0.3333)

    def test_stable_observations_are_usable(self) -> None:
        observations = [
            _observation(1, scl=1.0, mndwi=1.05, ndwi=0.98),
            _observation(2, scl=1.1, mndwi=1.12, ndwi=1.04),
            _observation(3, scl=1.2, mndwi=1.18, ndwi=1.10),
        ]

        assessment = assess_observation_quality(
            observations,
            passport_area_km2=1.2,
        )

        self.assertEqual(assessment.status, "USE")
        self.assertEqual(assessment.issues, [])

    def test_extreme_area_ratio_requires_roi_review(self) -> None:
        observations = [
            _observation(1, scl=3.5, mndwi=3.6, ndwi=3.4),
            _observation(2, scl=3.7, mndwi=3.8, ndwi=3.6),
            _observation(3, scl=3.9, mndwi=4.0, ndwi=3.8),
        ]

        assessment = assess_observation_quality(
            observations,
            passport_area_km2=1.0,
        )

        self.assertEqual(assessment.status, "FIX_ROI_OR_USE_CAUTION")
        self.assertTrue(any("passport area" in issue for issue in assessment.issues))

    def test_short_low_signal_series_is_excluded(self) -> None:
        observations = [
            _observation(1, scl=0, mndwi=0, ndwi=0),
            _observation(2, scl=0, mndwi=0, ndwi=0),
        ]

        assessment = assess_observation_quality(
            observations,
            passport_area_km2=1.0,
        )

        self.assertEqual(assessment.status, "EXCLUDE_LOW_SIGNAL")
        self.assertGreaterEqual(len(assessment.issues), 2)
