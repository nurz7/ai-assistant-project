import requests

from app.config import settings


def generate_mock_answer(message: str) -> str:
    return (
        "This is a mock AI response. "
        "The assistant received your message and will later use a real LLM API. "
        f"Your message: {message}"
    )


def generate_llm_answer(message: str) -> str:
    """
    Generates an answer using either mock mode or an OpenAI-compatible LLM API.
    Mock mode is used by default so the project works without an API key.
    """

    if settings.LLM_PROVIDER == "mock":
        return generate_mock_answer(message)

    if not settings.LLM_API_KEY:
        return "LLM_API_KEY is missing. Please add it to your .env file."

    if not settings.LLM_BASE_URL:
        return "LLM_BASE_URL is missing. Please add it to your .env file."

    payload = {
        "model": settings.LLM_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an internal AI Operations Assistant. "
                    "You help employees with documents, business workflows, "
                    "data questions and short operational reports. "
                    "Answer clearly and concisely."
                )
            },
            {
                "role": "user",
                "content": message
            }
        ],
        "temperature": 0.2
    }

    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            settings.LLM_BASE_URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"]

    except requests.exceptions.RequestException as error:
        return f"LLM request failed: {error}"

    except KeyError:
        return "LLM response format is unexpected."
