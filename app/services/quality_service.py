from pathlib import Path
from statistics import mean, median

from app.models.schemas import QualityAssessment, ReservoirObservation
from app.services.reservoir_service import get_observations, get_reservoir_summary

MIN_DATES = 3
MIN_NONZERO_DATES = 2
ZERO_AREA_EXCLUDE_SHARE = 0.60
LOW_MEDIAN_PASSPORT_RATIO = 0.05
HIGH_MEDIAN_PASSPORT_RATIO = 1.50
EXTREME_MAX_PASSPORT_RATIO = 3.00
HIGH_RATIO_THRESHOLD = 2.00
HIGH_RATIO_SHARE_FOR_ROI_REVIEW = 0.25
HIGH_CLOUD_THRESHOLD = 40.0
HIGH_CLOUD_CAUTION_SHARE = 0.25
METHOD_CONFLICT_THRESHOLD = 20.0
METHOD_CONFLICT_CAUTION_SHARE = 0.25

STATUS_DECISIONS = {
    "USE": "Use in the demo analysis with standard methodology limitations.",
    "USE_WITH_CAUTION": "Use with caution and review the flagged observations.",
    "FIX_ROI_OR_USE_CAUTION": (
        "Review or reduce the ROI before relying on the area time series."
    ),
    "EXCLUDE_LOW_SIGNAL": (
        "Exclude from the main analysis until more usable observations are available."
    ),
}


def assess_reservoir_quality(
    reservoir_name: str,
    *,
    start_date: str | None = None,
    end_date: str | None = None,
    db_path: Path | None = None,
) -> QualityAssessment | None:
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

    return assess_observation_quality(
        observations,
        passport_area_km2=reservoir.passport_area_km2,
    )


def assess_observation_quality(
    observations: list[ReservoirObservation],
    *,
    passport_area_km2: float | None,
) -> QualityAssessment:
    if not observations:
        raise ValueError("At least one observation is required")

    areas = [observation.mndwi_area_km2 for observation in observations]
    dates_count = len(observations)
    nonzero_dates = sum(area > 0 for area in areas)
    zero_area_share = (dates_count - nonzero_dates) / dates_count
    high_cloud_share = (
        sum(
            observation.cloud_percent >= HIGH_CLOUD_THRESHOLD
            for observation in observations
        )
        / dates_count
    )
    method_conflict_share = (
        sum(_has_method_conflict(observation) for observation in observations)
        / dates_count
    )

    ratios = (
        [area / passport_area_km2 for area in areas]
        if passport_area_km2 is not None and passport_area_km2 > 0
        else []
    )
    median_ratio = median(ratios) if ratios else None
    max_ratio = max(ratios) if ratios else None
    high_ratio_share = (
        sum(ratio > HIGH_RATIO_THRESHOLD for ratio in ratios) / dates_count
        if ratios
        else 0.0
    )

    exclusion_issues = _exclusion_issues(
        dates_count,
        nonzero_dates,
        zero_area_share,
    )
    roi_issues = _roi_issues(max_ratio, high_ratio_share)
    caution_issues = _caution_issues(
        high_cloud_share,
        method_conflict_share,
        median_ratio,
    )

    if exclusion_issues:
        status = "EXCLUDE_LOW_SIGNAL"
        issues = exclusion_issues + roi_issues + caution_issues
    elif roi_issues:
        status = "FIX_ROI_OR_USE_CAUTION"
        issues = roi_issues + caution_issues
    elif caution_issues:
        status = "USE_WITH_CAUTION"
        issues = caution_issues
    else:
        status = "USE"
        issues = []

    return QualityAssessment(
        status=status,
        decision=STATUS_DECISIONS[status],
        dates_count=dates_count,
        nonzero_dates=nonzero_dates,
        zero_area_share=round(zero_area_share, 4),
        high_cloud_share=round(high_cloud_share, 4),
        method_conflict_share=round(method_conflict_share, 4),
        mean_area_km2=round(mean(areas), 4),
        median_area_km2=round(median(areas), 4),
        max_area_km2=round(max(areas), 4),
        median_ratio_to_passport=(
            round(median_ratio, 4) if median_ratio is not None else None
        ),
        max_ratio_to_passport=(round(max_ratio, 4) if max_ratio is not None else None),
        issues=issues,
    )


def _has_method_conflict(observation: ReservoirObservation) -> bool:
    areas = (
        observation.scl_water_area_km2,
        observation.mndwi_area_km2,
        observation.ndwi_area_km2,
    )
    mean_area = mean(areas)
    if mean_area == 0:
        return False
    spread_percent = ((max(areas) - min(areas)) / mean_area) * 100
    return spread_percent >= METHOD_CONFLICT_THRESHOLD


def _exclusion_issues(
    dates_count: int,
    nonzero_dates: int,
    zero_area_share: float,
) -> list[str]:
    issues: list[str] = []
    if dates_count < MIN_DATES:
        issues.append(f"Only {dates_count} observation dates are available.")
    if nonzero_dates < MIN_NONZERO_DATES:
        issues.append(
            f"Only {nonzero_dates} non-zero water observations are available."
        )
    if zero_area_share >= ZERO_AREA_EXCLUDE_SHARE:
        issues.append(f"Zero-area share is {zero_area_share:.1%}.")
    return issues


def _roi_issues(
    max_ratio: float | None,
    high_ratio_share: float,
) -> list[str]:
    issues: list[str] = []
    if max_ratio is not None and max_ratio > EXTREME_MAX_PASSPORT_RATIO:
        issues.append(f"Maximum area is {max_ratio:.2f}x passport area.")
    if high_ratio_share > HIGH_RATIO_SHARE_FOR_ROI_REVIEW:
        issues.append(
            f"Area exceeds 2x passport area on {high_ratio_share:.1%} of dates."
        )
    return issues


def _caution_issues(
    high_cloud_share: float,
    method_conflict_share: float,
    median_ratio: float | None,
) -> list[str]:
    issues: list[str] = []
    if high_cloud_share > HIGH_CLOUD_CAUTION_SHARE:
        issues.append(f"High cloud affects {high_cloud_share:.1%} of observations.")
    if method_conflict_share > METHOD_CONFLICT_CAUTION_SHARE:
        issues.append(
            "SCL, MNDWI, and NDWI conflict on "
            f"{method_conflict_share:.1%} of observations."
        )
    if median_ratio is not None and median_ratio < LOW_MEDIAN_PASSPORT_RATIO:
        issues.append("Median area is below 5% of passport area.")
    if median_ratio is not None and median_ratio > HIGH_MEDIAN_PASSPORT_RATIO:
        issues.append("Median area is above 1.5x passport area.")
    return issues
