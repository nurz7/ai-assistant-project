# Demo Quality Rules

## Purpose

The quality service adapts dimensions found in the owner's dissertation workflow into deterministic portfolio-MVP checks. These rules support analyst review; they are not scientifically validated operational thresholds.

## Input Metrics

- number of observation dates;
- number and share of non-zero MNDWI areas;
- mean, median, and maximum MNDWI area;
- median and maximum ratio to passport area;
- share of dates above two times passport area;
- share of high-cloud observations;
- share of observations where SCL, MNDWI, and NDWI disagree materially.

## Demo Decisions

`EXCLUDE_LOW_SIGNAL` is returned when fewer than three dates exist, fewer than two dates have non-zero water area, or at least 60% of dates have zero area.

`FIX_ROI_OR_USE_CAUTION` is returned when maximum area exceeds three times passport area or more than 25% of dates exceed two times passport area.

`USE_WITH_CAUTION` is returned when more than 25% of observations have at least 40% cloud, more than 25% have a method spread of at least 20%, median area is below 5% of passport area, or median area is above 1.5 times passport area.

`USE` is returned when none of the preceding checks produces an issue.

Exclusion has priority over ROI review, which has priority over caution. Every non-`USE` result includes human-readable reasons.

## Limitations

The thresholds are transparent engineering defaults selected for the synthetic demo. They must be calibrated and validated before use with real reservoirs. A status never establishes an exact water level or replaces source-image review.
