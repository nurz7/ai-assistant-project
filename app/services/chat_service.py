import re

from app.models.schemas import ChatIntent, ChatResponse, SourceReference
from app.services.llm_client import generate_llm_answer, get_llm_mode
from app.services.retrieval_service import retrieve_relevant_chunks

UNSUPPORTED_ANSWER = (
    "I don't have enough information in the reservoir monitoring knowledge base "
    "or demo data to answer this question."
)
NO_CONTEXT_WARNING = "No relevant reservoir monitoring methodology context was found."
STRUCTURED_DATA_WARNING = (
    "Reservoir observation tools are not implemented yet. This MVP currently "
    "supports methodology RAG through the chat endpoint."
)

OBSERVATION_PATTERN = re.compile(
    r"\b(observation|observations|observed|show|date|period|may 2025)\b",
    re.IGNORECASE,
)
REPORT_PATTERN = re.compile(r"\b(report|summary)\b", re.IGNORECASE)
RESERVOIR_PATTERN = re.compile(r"\b(reservoir|tasmola)\b", re.IGNORECASE)


def classify_intent(message: str) -> ChatIntent:
    normalized = message.strip().lower()
    if REPORT_PATTERN.search(normalized):
        return "report_generation"
    if OBSERVATION_PATTERN.search(normalized):
        return "observation_analysis"
    if RESERVOIR_PATTERN.search(normalized) and not any(
        term in normalized
        for term in (
            "sentinel",
            "ndwi",
            "mndwi",
            "scl",
            "cloud",
            "roi",
            "water mask",
            "passport area",
            "normal level",
            "dead level",
            "area-level",
            "method",
            "methodology",
        )
    ):
        return "reservoir_lookup"
    return "methodology_qa"


async def process_chat(message: str) -> ChatResponse:
    """Run the chat workflow and build the public API response."""

    intent = classify_intent(message)
    if intent in {"reservoir_lookup", "observation_analysis", "report_generation"}:
        return ChatResponse(
            user_message=message,
            answer=UNSUPPORTED_ANSWER,
            mode=get_llm_mode(),
            intent="unsupported",
            warnings=[STRUCTURED_DATA_WARNING],
        )

    search_results = retrieve_relevant_chunks(message)
    if not search_results:
        return ChatResponse(
            user_message=message,
            answer=UNSUPPORTED_ANSWER,
            mode=get_llm_mode(),
            intent="unsupported",
            warnings=[NO_CONTEXT_WARNING],
        )

    context_chunks = [result.chunk for result in search_results]
    answer = await generate_llm_answer(message, context_chunks)
    sources = [
        SourceReference(
            document=chunk.document,
            section=chunk.section,
            chunk_id=chunk.chunk_id,
        )
        for chunk in context_chunks
    ]

    return ChatResponse(
        user_message=message,
        answer=answer,
        mode=get_llm_mode(),
        intent=intent,
        sources=sources,
    )
