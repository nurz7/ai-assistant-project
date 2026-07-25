import json
import unittest

from app.core.observability import log_chat_completed, log_chat_failed
from app.models.schemas import ChatResponse, SourceReference


class ObservabilityTests(unittest.TestCase):
    def test_completed_event_contains_safe_structured_metadata(self) -> None:
        response = ChatResponse(
            user_message="Sensitive request content",
            answer="Sensitive answer content",
            mode="mock",
            intent="methodology_qa",
            sources=[
                SourceReference(
                    document="method.md",
                    section="Method",
                    chunk_id="method-1",
                )
            ],
            warnings=["Demo warning"],
        )

        with self.assertLogs("app.core.observability", level="INFO") as captured:
            log_chat_completed(
                run_id="run-123",
                duration_ms=12.34,
                response=response,
            )

        record = captured.output[0]
        event = json.loads(record.split("chat_event=", maxsplit=1)[1])
        self.assertEqual(event["event"], "chat_completed")
        self.assertEqual(event["run_id"], "run-123")
        self.assertEqual(event["duration_ms"], 12.34)
        self.assertEqual(event["intent"], "methodology_qa")
        self.assertEqual(event["source_count"], 1)
        self.assertEqual(event["status_code"], 200)
        self.assertNotIn("Sensitive request content", record)
        self.assertNotIn("Sensitive answer content", record)

    def test_failure_event_excludes_error_details(self) -> None:
        with self.assertLogs("app.core.observability", level="INFO") as captured:
            log_chat_failed(
                run_id="run-456",
                duration_ms=3.0,
                status_code=502,
                error_type="LLMProviderError",
            )

        event = json.loads(captured.output[0].split("chat_event=", maxsplit=1)[1])
        self.assertEqual(event["event"], "chat_failed")
        self.assertEqual(event["status_code"], 502)
        self.assertEqual(event["error_type"], "LLMProviderError")
