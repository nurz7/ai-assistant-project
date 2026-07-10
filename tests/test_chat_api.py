import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from pydantic import ValidationError

from app.api.routes import chat as chat_route
from app.main import app, home
from app.models.schemas import ChatRequest, ChatResponse
from app.services.llm_client import LLMConfigurationError, LLMProviderError


class ChatApiTests(unittest.TestCase):
    def test_chat_route_is_registered(self) -> None:
        self.assertIn("/chat", app.openapi()["paths"])

    def test_home_reports_application_status(self) -> None:
        self.assertEqual(
            asyncio.run(home()),
            {
                "message": "AI/GIS Copilot for Reservoir Monitoring is running",
                "status": "ok",
                "version": "0.4.0",
            },
        )

    def test_chat_returns_structured_mock_response(self) -> None:
        service_response = ChatResponse(
            user_message="What is MNDWI used for?",
            answer="Mock answer",
            mode="mock",
            intent="methodology_qa",
        )
        request = ChatRequest(message="  What is MNDWI used for?  ")

        with patch.object(
            chat_route,
            "process_chat",
            AsyncMock(return_value=service_response),
        ) as process_chat_mock:
            response = asyncio.run(chat_route.chat(request))

        self.assertEqual(response, service_response)
        process_chat_mock.assert_called_once_with("What is MNDWI used for?")

    def test_chat_rejects_blank_message(self) -> None:
        with self.assertRaises(ValidationError):
            ChatRequest(message="   ")

    def test_chat_rejects_message_over_limit(self) -> None:
        with self.assertRaises(ValidationError):
            ChatRequest(message="x" * 4_001)

    def test_chat_maps_configuration_error_to_service_unavailable(self) -> None:
        request = ChatRequest(message="test")

        with patch.object(
            chat_route,
            "process_chat",
            AsyncMock(
                side_effect=LLMConfigurationError(
                    "LLM_API_KEY is required in LLM mode."
                )
            ),
        ):
            with self.assertRaises(HTTPException) as raised:
                asyncio.run(chat_route.chat(request))

        self.assertEqual(raised.exception.status_code, 503)
        self.assertEqual(
            raised.exception.detail, "LLM_API_KEY is required in LLM mode."
        )

    def test_chat_maps_provider_error_to_bad_gateway(self) -> None:
        request = ChatRequest(message="test")

        with patch.object(
            chat_route,
            "process_chat",
            AsyncMock(side_effect=LLMProviderError("private provider details")),
        ):
            with self.assertRaises(HTTPException) as raised:
                asyncio.run(chat_route.chat(request))

        self.assertEqual(raised.exception.status_code, 502)
        self.assertEqual(
            raised.exception.detail,
            "The language model provider is temporarily unavailable.",
        )
