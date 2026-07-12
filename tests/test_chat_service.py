import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from app.models.documents import DocumentChunk, SearchResult
from app.models.schemas import (
    AnomalyFlag,
    CalculationResult,
    QualityAssessment,
    ReservoirObservation,
    ReservoirReference,
)
from app.services import chat_service
from app.services.report_service import MonitoringReport


class ChatServiceTests(unittest.TestCase):
    def test_process_chat_builds_structured_response(self) -> None:
        chunk = DocumentChunk(
            document="sentinel2_water_detection.md",
            title="Sentinel-2 Water Detection Methodology",
            section="MNDWI Water Mask",
            chunk_id="sentinel2-water-detection-mndwi-water-mask-001",
            content="MNDWI is a modified water index used for water detection.",
        )
        with (
            patch.object(
                chat_service,
                "retrieve_relevant_chunks",
                return_value=[SearchResult(chunk=chunk, score=1.0)],
            ),
            patch.object(
                chat_service,
                "generate_llm_answer",
                AsyncMock(return_value="Generated answer"),
            ) as generate_mock,
            patch.object(chat_service, "get_llm_mode", return_value="mock"),
        ):
            response = asyncio.run(chat_service.process_chat("test question"))

        self.assertEqual(
            response.model_dump(),
            {
                "user_message": "test question",
                "answer": "Generated answer",
                "mode": "mock",
                "intent": "methodology_qa",
                "sources": [
                    {
                        "document": "sentinel2_water_detection.md",
                        "section": "MNDWI Water Mask",
                        "chunk_id": ("sentinel2-water-detection-mndwi-water-mask-001"),
                    }
                ],
                "reservoir": None,
                "calculation_result": None,
                "observations": [],
                "anomaly_flags": [],
                "quality_assessment": None,
                "warnings": [],
            },
        )
        generate_mock.assert_called_once_with("test question", [chunk])

    def test_process_chat_refuses_when_context_is_missing(self) -> None:
        with (
            patch.object(
                chat_service,
                "retrieve_relevant_chunks",
                return_value=[],
            ),
            patch.object(
                chat_service, "generate_llm_answer", AsyncMock()
            ) as generate_mock,
            patch.object(chat_service, "get_llm_mode", return_value="mock"),
        ):
            response = asyncio.run(chat_service.process_chat("unsupported question"))

        self.assertEqual(response.answer, chat_service.UNSUPPORTED_ANSWER)
        self.assertEqual(response.intent, "unsupported")
        self.assertEqual(response.sources, [])
        self.assertEqual(response.warnings, [chat_service.NO_CONTEXT_WARNING])
        generate_mock.assert_not_called()

    def test_process_chat_returns_monitoring_report(self) -> None:
        reservoir = ReservoirReference(
            name="Tasmola",
            region="Akmola Region",
            passport_area_km2=4.20,
        )
        report = MonitoringReport(
            text="# Monitoring Report: Tasmola",
            reservoir=reservoir,
            observations=[],
            calculation_result=None,
            anomaly_flags=[],
            quality_assessment=QualityAssessment(
                status="USE",
                decision="Use in demo.",
                dates_count=3,
                nonzero_dates=3,
                zero_area_share=0,
                high_cloud_share=0,
                method_conflict_share=0,
                mean_area_km2=3.9,
                median_area_km2=3.9,
                max_area_km2=4.0,
                median_ratio_to_passport=0.93,
                max_ratio_to_passport=0.95,
            ),
            sources=[],
            warnings=[chat_service.DEMO_DATA_WARNING],
        )
        with (
            patch.object(
                chat_service,
                "extract_reservoir_name",
                return_value="Tasmola",
            ),
            patch.object(chat_service, "build_monitoring_report", return_value=report),
            patch.object(chat_service, "get_llm_mode", return_value="mock"),
        ):
            response = asyncio.run(
                chat_service.process_chat(
                    "Generate a short monitoring report for Tasmola."
                )
            )

        self.assertEqual(response.intent, "report_generation")
        self.assertEqual(response.answer, "# Monitoring Report: Tasmola")
        self.assertEqual(response.reservoir, reservoir)
        self.assertEqual(response.quality_assessment.status, "USE")
        self.assertEqual(response.sources, [])
        self.assertEqual(response.warnings, [chat_service.DEMO_DATA_WARNING])

    def test_process_chat_returns_reservoir_profile(self) -> None:
        reservoir = ReservoirReference(
            name="Tasmola",
            region="Akmola Region",
            passport_area_km2=4.20,
            normal_level_m=352.4,
            dead_level_m=346.1,
            latitude=50.1234,
            longitude=71.4567,
            notes="Synthetic demo record.",
        )
        with (
            patch.object(
                chat_service,
                "extract_reservoir_name",
                return_value="Tasmola",
            ),
            patch.object(
                chat_service,
                "get_reservoir_summary",
                return_value=reservoir,
            ),
            patch.object(chat_service, "get_llm_mode", return_value="mock"),
        ):
            response = asyncio.run(chat_service.process_chat("Show Tasmola profile"))

        self.assertEqual(response.intent, "reservoir_lookup")
        self.assertEqual(response.reservoir, reservoir)
        self.assertIn("Passport area: 4.20 km2", response.answer)
        self.assertEqual(
            response.warnings,
            [chat_service.DEMO_DATA_WARNING, chat_service.WATER_LEVEL_WARNING],
        )

    def test_process_chat_returns_observation_analysis(self) -> None:
        reservoir = ReservoirReference(
            name="Tasmola",
            region="Akmola Region",
            passport_area_km2=4.20,
        )
        observation = ReservoirObservation(
            observation_id=1,
            observation_date="2025-05-03",
            source="Sentinel-2 L2A",
            scl_water_area_km2=3.82,
            mndwi_area_km2=3.94,
            ndwi_area_km2=3.75,
            cloud_percent=8.5,
            roi_area_km2=5.10,
            method_version="demo-v0.1",
        )
        calculation = CalculationResult(
            metric="mndwi_area_vs_passport_area_percent_difference",
            value=-6.19,
            unit="%",
            explanation="MNDWI area was lower than passport area.",
        )
        flag = AnomalyFlag(
            observation_id=1,
            observation_date="2025-05-03",
            alert_type="method_conflict",
            severity="medium",
            message="Synthetic flag.",
        )
        with (
            patch.object(
                chat_service,
                "extract_reservoir_name",
                return_value="Tasmola",
            ),
            patch.object(
                chat_service,
                "get_reservoir_summary",
                return_value=reservoir,
            ),
            patch.object(
                chat_service,
                "get_observations",
                return_value=[observation],
            ),
            patch.object(
                chat_service,
                "compare_area_to_passport",
                return_value=calculation,
            ),
            patch.object(
                chat_service,
                "find_area_anomalies",
                return_value=[flag],
            ),
            patch.object(chat_service, "get_llm_mode", return_value="mock"),
        ):
            response = asyncio.run(
                chat_service.process_chat("Show Tasmola observations for May 2025")
            )

        self.assertEqual(response.intent, "observation_analysis")
        self.assertEqual(response.observations, [observation])
        self.assertEqual(response.anomaly_flags, [flag])
        self.assertEqual(response.calculation_result, calculation)
        self.assertEqual(response.quality_assessment.status, "EXCLUDE_LOW_SIGNAL")
