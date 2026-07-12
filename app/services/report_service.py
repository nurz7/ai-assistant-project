from dataclasses import dataclass
from pathlib import Path

from app.models.schemas import (
    AnomalyFlag,
    CalculationResult,
    QualityAssessment,
    ReservoirObservation,
    ReservoirReference,
    SourceReference,
)
from app.services.quality_service import assess_observation_quality
from app.services.reservoir_service import (
    compare_area_to_passport,
    find_area_anomalies,
    get_observations,
    get_reservoir_summary,
)
from app.services.retrieval_service import retrieve_relevant_chunks

DEMO_DATA_WARNING = (
    "Reservoir records and satellite observations are synthetic demo data, not "
    "official operational records."
)
WATER_LEVEL_WARNING = (
    "Do not treat satellite-derived water area as an exact water level without "
    "a validated area-level relationship and human review."
)

REPORT_METHODOLOGY_QUERIES = (
    "What should a reservoir monitoring report include?",
    "Why does cloud filtering matter for satellite water detection?",
    "What limitations should be recorded with method version?",
    "Как выполняется автоматический контроль качества временных рядов воды?",
)


@dataclass(frozen=True)
class MonitoringReport:
    text: str
    reservoir: ReservoirReference
    observations: list[ReservoirObservation]
    calculation_result: CalculationResult | None
    anomaly_flags: list[AnomalyFlag]
    quality_assessment: QualityAssessment
    sources: list[SourceReference]
    warnings: list[str]


def build_monitoring_report(
    reservoir_name: str,
    *,
    start_date: str | None = None,
    end_date: str | None = None,
    db_path: Path | None = None,
    docs_path: Path | None = None,
) -> MonitoringReport | None:
    """Build a grounded report from synthetic observations and methodology."""

    reservoir = get_reservoir_summary(reservoir_name, db_path=db_path)
    if not reservoir:
        return None

    observations = get_observations(
        reservoir_name,
        start_date=start_date,
        end_date=end_date,
        db_path=db_path,
    )
    if not observations:
        return None

    calculation_result = compare_area_to_passport(
        reservoir_name,
        method="mndwi",
        start_date=start_date,
        end_date=end_date,
        db_path=db_path,
    )
    anomaly_flags = find_area_anomalies(
        reservoir_name,
        start_date=start_date,
        end_date=end_date,
        db_path=db_path,
    )
    quality_assessment = assess_observation_quality(
        observations,
        passport_area_km2=reservoir.passport_area_km2,
    )
    sources = _retrieve_report_sources(docs_path)
    warnings = [DEMO_DATA_WARNING, WATER_LEVEL_WARNING]
    text = _render_report(
        reservoir,
        observations,
        calculation_result,
        anomaly_flags,
        quality_assessment,
        sources,
        start_date=start_date,
        end_date=end_date,
    )

    return MonitoringReport(
        text=text,
        reservoir=reservoir,
        observations=observations,
        calculation_result=calculation_result,
        anomaly_flags=anomaly_flags,
        quality_assessment=quality_assessment,
        sources=sources,
        warnings=warnings,
    )


def _retrieve_report_sources(docs_path: Path | None) -> list[SourceReference]:
    sources: list[SourceReference] = []
    seen_chunk_ids: set[str] = set()
    for query in REPORT_METHODOLOGY_QUERIES:
        results = retrieve_relevant_chunks(query, docs_path=docs_path, top_k=1)
        if not results:
            continue
        chunk = results[0].chunk
        if chunk.chunk_id in seen_chunk_ids:
            continue
        seen_chunk_ids.add(chunk.chunk_id)
        sources.append(
            SourceReference(
                document=chunk.document,
                section=chunk.section,
                chunk_id=chunk.chunk_id,
            )
        )
    return sources


def _render_report(
    reservoir: ReservoirReference,
    observations: list[ReservoirObservation],
    calculation_result: CalculationResult | None,
    anomaly_flags: list[AnomalyFlag],
    quality_assessment: QualityAssessment,
    sources: list[SourceReference],
    *,
    start_date: str | None,
    end_date: str | None,
) -> str:
    period = _format_period(start_date, end_date, observations)
    lines = [
        f"# Monitoring Report: {reservoir.name}",
        "",
        "## Scope",
        f"- Period: {period}",
        f"- Region: {reservoir.region}",
        f"- Passport area: {_format_optional(reservoir.passport_area_km2)} km2",
        "- Data status: synthetic portfolio demo data",
        "",
        "## Sentinel-2 Observations",
    ]
    for observation in observations:
        lines.append(
            "- "
            f"{observation.observation_date}: SCL "
            f"{observation.scl_water_area_km2:.2f} km2; MNDWI "
            f"{observation.mndwi_area_km2:.2f} km2; NDWI "
            f"{observation.ndwi_area_km2:.2f} km2; cloud "
            f"{observation.cloud_percent:.1f}%; ROI "
            f"{observation.roi_area_km2:.2f} km2; method "
            f"{observation.method_version}."
        )

    lines.extend(["", "## Passport-Area Comparison"])
    if calculation_result:
        lines.append(
            f"- {calculation_result.explanation} "
            f"Difference: {calculation_result.value:.2f}{calculation_result.unit}."
        )
    else:
        lines.append("- No comparison was available for the selected period.")

    lines.extend(["", "## Issues Requiring Review"])
    if anomaly_flags:
        for flag in anomaly_flags:
            date_prefix = f"{flag.observation_date}: " if flag.observation_date else ""
            lines.append(f"- [{flag.severity.upper()}] {date_prefix}{flag.message}")
    else:
        lines.append("- No threshold-based anomaly flags were found.")

    qc_citation = _citation_for_section(sources, "Automatic Quality Control")
    lines.extend(
        [
            "",
            "## Automatic Quality Control",
            f"- Status: {quality_assessment.status}{qc_citation}",
            f"- Decision: {quality_assessment.decision}",
            (
                f"- Dates: {quality_assessment.dates_count}; non-zero dates: "
                f"{quality_assessment.nonzero_dates}; high-cloud share: "
                f"{quality_assessment.high_cloud_share:.1%}; method-conflict share: "
                f"{quality_assessment.method_conflict_share:.1%}."
            ),
        ]
    )
    for issue in quality_assessment.issues:
        lines.append(f"- QC issue: {issue}")

    citation_suffix = _citation_for_section(sources, "Monitoring Report")
    limitation_suffix = _citation_for_section(sources, "Method Version and Limitations")
    lines.extend(
        [
            "",
            "## Method Notes",
            (
                "- Satellite-derived water area is an estimate from an ROI water "
                f"mask, not an official hydrological measurement.{citation_suffix}"
            ),
            (
                "- Cloud filtering, ROI quality, threshold choices, shoreline mixed "
                "pixels, method version, and disagreement between SCL, MNDWI, and "
                f"NDWI affect interpretation.{limitation_suffix}"
            ),
            "",
            "## Conclusion",
            f"- {_build_conclusion(anomaly_flags)}",
            (
                "- The available area estimates do not establish an exact water "
                "level. Human review is required for operational decisions."
            ),
            "",
            "## Sources",
        ]
    )
    if sources:
        for source in sources:
            lines.append(f"- [{source.chunk_id}] {source.document}, {source.section}")
    else:
        lines.append("- No methodology source was retrieved.")

    return "\n".join(lines)


def _format_period(
    start_date: str | None,
    end_date: str | None,
    observations: list[ReservoirObservation],
) -> str:
    if start_date and end_date and start_date != end_date:
        return f"{start_date} to {end_date}"
    if start_date:
        return start_date
    return f"{observations[0].observation_date} to {observations[-1].observation_date}"


def _citation_for_section(
    sources: list[SourceReference],
    section: str,
) -> str:
    source = next((item for item in sources if item.section == section), None)
    return f" [{source.chunk_id}]" if source else ""


def _format_optional(value: float | None) -> str:
    return f"{value:.2f}" if value is not None else "not available"


def _build_conclusion(anomaly_flags: list[AnomalyFlag]) -> str:
    if any(flag.severity == "high" for flag in anomaly_flags):
        return (
            "At least one observation has a high-severity quality or area flag and "
            "should be reviewed before interpretation."
        )
    if anomaly_flags:
        return (
            "The selected observations contain anomaly flags that should be checked "
            "against the source imagery and processing settings."
        )
    return "The selected observations contain no threshold-based anomaly flags."
