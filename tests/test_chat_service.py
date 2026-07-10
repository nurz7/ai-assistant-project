import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from app.models.documents import DocumentChunk, SearchResult
from app.services import chat_service


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
                        "chunk_id": (
                            "sentinel2-water-detection-mndwi-water-mask-001"
                        ),
                    }
                ],
                "reservoir": None,
                "calculation_result": None,
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

    def test_process_chat_returns_structured_data_warning_for_report_request(self) -> None:
        with (
            patch.object(
                chat_service,
                "retrieve_relevant_chunks",
                return_value=[],
            ) as retrieve_mock,
            patch.object(
                chat_service, "generate_llm_answer", AsyncMock()
            ) as generate_mock,
            patch.object(chat_service, "get_llm_mode", return_value="mock"),
        ):
            response = asyncio.run(
                chat_service.process_chat(
                    "Generate a short monitoring report for Tasmola."
                )
            )

        self.assertEqual(response.intent, "unsupported")
        self.assertEqual(response.sources, [])
        self.assertEqual(response.warnings, [chat_service.STRUCTURED_DATA_WARNING])
        retrieve_mock.assert_not_called()
        generate_mock.assert_not_called()
