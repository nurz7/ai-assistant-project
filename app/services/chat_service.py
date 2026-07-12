import re
from calendar import monthrange

from app.models.schemas import ChatIntent, ChatResponse, SourceReference
from app.services.llm_client import generate_llm_answer, get_llm_mode
from app.services.reservoir_service import (
    compare_area_to_passport,
    extract_reservoir_name,
    find_area_anomalies,
    get_observations,
    get_reservoir_summary,
)
from app.services.retrieval_service import retrieve_relevant_chunks

UNSUPPORTED_ANSWER = (
    "I don't have enough information in the reservoir monitoring knowledge base "
    "or demo data to answer this question."
)
NO_CONTEXT_WARNING = "No relevant reservoir monitoring methodology context was found."
REPORT_GENERATION_WARNING = (
    "Monitoring report generation is planned for Phase 4. The current MVP can "
    "return methodology answers, reservoir profiles, observations, comparisons, "
    "and anomaly flags from synthetic demo data."
)
UNKNOWN_RESERVOIR_WARNING = "No matching reservoir was found in the synthetic demo data."
NO_OBSERVATIONS_WARNING = "No matching satellite observations were found."
DEMO_DATA_WARNING = (
    "Reservoir records and satellite observations are synthetic demo data, not "
    "official operational records."
)
WATER_LEVEL_WARNING = (
    "Do not treat satellite-derived water area as an exact water level without "
    "a validated area-level relationship and human review."
)

OBSERVATION_PATTERN = re.compile(
    r"\b(observation|observations|observed|date|period|latest|"
    r"compare|passport|anomaly|anomalies|suspicious|may 2025)\b",
    re.IGNORECASE,
)
REPORT_PATTERN = re.compile(r"\b(generate|create|write)\b.*\breport\b", re.IGNORECASE)
METHODOLOGY_QUESTION_PATTERN = re.compile(
    r"^\s*(what|why|how|which|define|explain)\b",
    re.IGNORECASE,
)
RESERVOIR_PATTERN = re.compile(r"\b(reservoir|tasmola)\b", re.IGNORECASE)
ISO_DATE_PATTERN = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")
MONTH_YEAR_PATTERN = re.compile(
    r"\b("
    r"january|february|march|april|may|june|july|august|september|october|"
    r"november|december"
    r")\s+(20\d{2})\b",
    re.IGNORECASE,
)
MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def classify_intent(message: str) -> ChatIntent:
    normalized = message.strip().lower()
    structured_terms = (
        "show",
        "list",
        "get observations",
        "observation",
        "observations",
        "compare",
        "find",
        "latest",
        "anomaly",
        "anomalies",
        "date",
        "period",
    )
    if METHODOLOGY_QUESTION_PATTERN.search(normalized) and not any(
        term in normalized for term in structured_terms
    ):
        return "methodology_qa"
    if REPORT_PATTERN.search(normalized):
        return "report_generation"
    if OBSERVATION_PATTERN.search(normalized):
        return "observation_analysis"
    reservoir_name = extract_reservoir_name(normalized)
    if reservoir_name or (
        RESERVOIR_PATTERN.search(normalized)
        and not any(
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
        )
    ):
        return "reservoir_lookup"
    return "methodology_qa"


async def process_chat(message: str) -> ChatResponse:
    """Run the chat workflow and build the public API response."""

    intent = classify_intent(message)
    if intent == "report_generation":
        return ChatResponse(
            user_message=message,
            answer=UNSUPPORTED_ANSWER,
            mode=get_llm_mode(),
            intent="unsupported",
            warnings=[REPORT_GENERATION_WARNING],
        )
    if intent == "reservoir_lookup":
        return _handle_reservoir_lookup(message)
    if intent == "observation_analysis":
        return _handle_observation_analysis(message)

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


def _handle_reservoir_lookup(message: str) -> ChatResponse:
    reservoir_name = extract_reservoir_name(message)
    if not reservoir_name:
        return ChatResponse(
            user_message=message,
            answer=UNSUPPORTED_ANSWER,
            mode=get_llm_mode(),
            intent="unsupported",
            warnings=[UNKNOWN_RESERVOIR_WARNING],
        )

    reservoir = get_reservoir_summary(reservoir_name)
    if not reservoir:
        return ChatResponse(
            user_message=message,
            answer=UNSUPPORTED_ANSWER,
            mode=get_llm_mode(),
            intent="unsupported",
            warnings=[UNKNOWN_RESERVOIR_WARNING],
        )

    answer = (
        "Reservoir profile from the synthetic demo database:\n\n"
        f"- Reservoir: {reservoir.name}\n"
        f"- Region: {reservoir.region}\n"
        f"- Passport area: {reservoir.passport_area_km2:.2f} km2\n"
        f"- Normal level: {reservoir.normal_level_m:.2f} m\n"
        f"- Dead level: {reservoir.dead_level_m:.2f} m\n"
        f"- Coordinates: {reservoir.latitude:.4f}, {reservoir.longitude:.4f}\n"
        f"- Notes: {reservoir.notes}"
    )
    return ChatResponse(
        user_message=message,
        answer=answer,
        mode=get_llm_mode(),
        intent="reservoir_lookup",
        reservoir=reservoir,
        warnings=[DEMO_DATA_WARNING, WATER_LEVEL_WARNING],
    )


def _handle_observation_analysis(message: str) -> ChatResponse:
    reservoir_name = extract_reservoir_name(message)
    if not reservoir_name:
        return ChatResponse(
            user_message=message,
            answer=UNSUPPORTED_ANSWER,
            mode=get_llm_mode(),
            intent="unsupported",
            warnings=[UNKNOWN_RESERVOIR_WARNING],
        )

    reservoir = get_reservoir_summary(reservoir_name)
    if not reservoir:
        return ChatResponse(
            user_message=message,
            answer=UNSUPPORTED_ANSWER,
            mode=get_llm_mode(),
            intent="unsupported",
            warnings=[UNKNOWN_RESERVOIR_WARNING],
        )

    start_date, end_date = _parse_date_range(message)
    observations = get_observations(
        reservoir_name,
        start_date=start_date,
        end_date=end_date,
    )
    if not observations:
        return ChatResponse(
            user_message=message,
            answer=(
                f"No satellite observations were found for {reservoir.name}"
                f"{_format_period_suffix(start_date, end_date)}."
            ),
            mode=get_llm_mode(),
            intent="observation_analysis",
            reservoir=reservoir,
            warnings=[NO_OBSERVATIONS_WARNING, DEMO_DATA_WARNING],
        )

    calculation_result = compare_area_to_passport(
        reservoir_name,
        method="mndwi",
        start_date=start_date,
        end_date=end_date,
    )
    anomaly_flags = find_area_anomalies(
        reservoir_name,
        start_date=start_date,
        end_date=end_date,
    )
    answer = _build_observation_answer(
        reservoir.name,
        observations,
        calculation_result,
        anomaly_count=len(anomaly_flags),
        start_date=start_date,
        end_date=end_date,
    )

    return ChatResponse(
        user_message=message,
        answer=answer,
        mode=get_llm_mode(),
        intent="observation_analysis",
        reservoir=reservoir,
        calculation_result=calculation_result,
        observations=observations,
        anomaly_flags=anomaly_flags,
        warnings=[DEMO_DATA_WARNING, WATER_LEVEL_WARNING],
    )


def _parse_date_range(message: str) -> tuple[str | None, str | None]:
    iso_dates = ISO_DATE_PATTERN.findall(message)
    if len(iso_dates) >= 2:
        ordered_dates = sorted(iso_dates[:2])
        return ordered_dates[0], ordered_dates[1]
    if len(iso_dates) == 1:
        return iso_dates[0], iso_dates[0]

    month_match = MONTH_YEAR_PATTERN.search(message)
    if not month_match:
        return None, None

    month_name = month_match.group(1).lower()
    year = int(month_match.group(2))
    month = MONTHS[month_name]
    last_day = monthrange(year, month)[1]
    return f"{year:04d}-{month:02d}-01", f"{year:04d}-{month:02d}-{last_day:02d}"


def _format_period_suffix(start_date: str | None, end_date: str | None) -> str:
    if start_date and end_date and start_date != end_date:
        return f" from {start_date} to {end_date}"
    if start_date:
        return f" on {start_date}"
    return ""


def _build_observation_answer(
    reservoir_name: str,
    observations,
    calculation_result,
    *,
    anomaly_count: int,
    start_date: str | None,
    end_date: str | None,
) -> str:
    lines = [
        (
            f"Found {len(observations)} synthetic Sentinel-2 observations for "
            f"{reservoir_name}{_format_period_suffix(start_date, end_date)}."
        )
    ]
    for observation in observations:
        lines.append(
            "- "
            f"{observation.observation_date}: SCL {observation.scl_water_area_km2:.2f} "
            f"km2, MNDWI {observation.mndwi_area_km2:.2f} km2, NDWI "
            f"{observation.ndwi_area_km2:.2f} km2, cloud "
            f"{observation.cloud_percent:.1f}%, method "
            f"{observation.method_version}."
        )

    if calculation_result:
        lines.append(f"\nLatest passport-area comparison: {calculation_result.explanation}")
    lines.append(f"Anomaly flags found: {anomaly_count}.")
    return "\n".join(lines)
