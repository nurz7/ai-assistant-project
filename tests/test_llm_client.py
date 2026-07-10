import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import httpx
from openai import APIConnectionError

from app.models.documents import DocumentChunk
from app.services import llm_client


class LLMClientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.provider_settings = SimpleNamespace(
            llm_api_key="test-key",
            llm_base_url="",
            llm_model="test-model",
        )
        self.context_chunks = [
            DocumentChunk(
                document="sentinel2_water_detection.md",
                title="Sentinel-2 Water Detection Methodology",
                section="MNDWI Water Mask",
                chunk_id="sentinel2-water-detection-mndwi-water-mask-001",
                content="MNDWI is used for water surface detection.",
            )
        ]

    def test_provider_failure_is_normalized(self) -> None:
        create_response = AsyncMock(
            side_effect=APIConnectionError(
                message="provider timeout",
                request=httpx.Request("POST", "https://example.test/v1/responses"),
            )
        )
        client = SimpleNamespace(responses=SimpleNamespace(create=create_response))

        with (
            patch.object(llm_client, "get_llm_mode", return_value="llm"),
            patch.object(llm_client, "settings", self.provider_settings),
            patch.object(llm_client, "_create_openai_client", return_value=client),
        ):
            with self.assertRaisesRegex(llm_client.LLMProviderError, "request failed"):
                asyncio.run(llm_client.generate_llm_answer("test", self.context_chunks))

    def test_unexpected_provider_response_is_normalized(self) -> None:
        response = SimpleNamespace(output_text="")
        create_response = AsyncMock(return_value=response)
        client = SimpleNamespace(responses=SimpleNamespace(create=create_response))

        with (
            patch.object(llm_client, "get_llm_mode", return_value="llm"),
            patch.object(llm_client, "settings", self.provider_settings),
            patch.object(llm_client, "_create_openai_client", return_value=client),
        ):
            with self.assertRaisesRegex(
                llm_client.LLMProviderError, "empty or invalid"
            ):
                asyncio.run(llm_client.generate_llm_answer("test", self.context_chunks))

    def test_mock_answer_contains_retrieved_content_and_citation(self) -> None:
        with patch.object(llm_client, "get_llm_mode", return_value="mock"):
            answer = asyncio.run(
                llm_client.generate_llm_answer("test", self.context_chunks)
            )

        self.assertIn("MNDWI is used for water surface detection.", answer)
        self.assertIn("[sentinel2-water-detection-mndwi-water-mask-001]", answer)

    def test_responses_api_request_is_grounded_and_not_stored(self) -> None:
        response = SimpleNamespace(
            output_text="Grounded answer [sentinel2-water-detection-mndwi-water-mask-001]"
        )
        create_response = AsyncMock(return_value=response)
        client = SimpleNamespace(responses=SimpleNamespace(create=create_response))

        with (
            patch.object(llm_client, "get_llm_mode", return_value="llm"),
            patch.object(llm_client, "settings", self.provider_settings),
            patch.object(llm_client, "_create_openai_client", return_value=client),
        ):
            answer = asyncio.run(
                llm_client.generate_llm_answer("test", self.context_chunks)
            )

        self.assertEqual(
            answer,
            "Grounded answer [sentinel2-water-detection-mndwi-water-mask-001]",
        )
        request = create_response.await_args.kwargs
        self.assertEqual(request["model"], "test-model")
        self.assertFalse(request["store"])
        self.assertEqual(request["reasoning"], {"effort": "low"})
        self.assertIn("MNDWI is used for water surface detection.", request["input"])
        self.assertIn("AI/GIS Copilot for Reservoir Monitoring", request["instructions"])
