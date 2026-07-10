import asyncio
import json
import unittest
from typing import Any

from app.main import app


async def request_app(
    method: str,
    path: str,
    *,
    json_body: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any]]:
    body = json.dumps(json_body).encode() if json_body is not None else b""
    headers = [(b"host", b"testserver")]
    if json_body is not None:
        headers.extend(
            [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode()),
            ]
        )

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "root_path": "",
        "headers": headers,
        "client": ("testclient", 50_000),
        "server": ("testserver", 80),
        "state": {},
    }
    request_sent = False
    messages: list[dict[str, Any]] = []

    async def receive() -> dict[str, Any]:
        nonlocal request_sent
        if not request_sent:
            request_sent = True
            return {"type": "http.request", "body": body, "more_body": False}
        return {"type": "http.disconnect"}

    async def send(message: dict[str, Any]) -> None:
        messages.append(message)

    await app(scope, receive, send)
    start = next(
        message for message in messages if message["type"] == "http.response.start"
    )
    response_body = b"".join(
        message.get("body", b"")
        for message in messages
        if message["type"] == "http.response.body"
    )
    return start["status"], json.loads(response_body)


class ChatIntegrationTests(unittest.TestCase):
    def test_supported_question_flows_through_asgi_app(self) -> None:
        status_code, data = asyncio.run(
            request_app(
                "POST",
                "/chat",
                json_body={
                    "message": "What is MNDWI used for in water surface detection?"
                },
            )
        )

        self.assertEqual(status_code, 200)
        self.assertEqual(data["mode"], "mock")
        self.assertEqual(data["intent"], "methodology_qa")
        self.assertEqual(data["sources"][0]["document"], "sentinel2_water_detection.md")

    def test_invalid_request_is_rejected_by_fastapi_validation(self) -> None:
        status_code, data = asyncio.run(
            request_app("POST", "/chat", json_body={"message": "   "})
        )

        self.assertEqual(status_code, 422)
        self.assertEqual(data["detail"][0]["type"], "value_error")
