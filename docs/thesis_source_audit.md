# Thesis Source Audit

## Purpose

This audit records how the owner-provided dissertation archive may be used in the public portfolio MVP.

## Reviewed Material

The archive contains a research report, staged CSV/XLSX outputs, charts, Google Earth Engine scripts, source tables, ROI coordinates, Sentinel-2 time series, automatic QC results, and preliminary S-H estimates.

## Approved for the Public MVP

- generalized Sentinel-2 processing workflow;
- flood-period window as a research-specific method parameter;
- SCL water class 6, NDWI, and MNDWI comparison methodology;
- ROI preparation and visual validation rules;
- raw-to-cleaned time-series workflow;
- quality-control dimensions and non-operational status categories;
- limitations of preliminary area-level estimation;
- public-safe literature references after independent source verification.

The approved methodology is summarized in `data/docs/thesis_satellite_pipeline.md`.

## Excluded from the Public MVP

- raw source tables from the dissertation archive;
- real object coordinates and ROI rectangles;
- real passport values and identifiers;
- real Sentinel-2 observation rows;
- preliminary calculated water levels;
- source PDFs whose redistribution rights have not been verified;
- personal and academic administrative information from the report cover page.

These materials may inform local analysis, but they must not be copied into the synthetic demo database or committed as public application data.

## Engineering Decision

The public application continues to use synthetic reservoir records. Thesis material strengthens methodology RAG, multilingual retrieval, evaluation cases, quality-control design, and future import schemas without changing the product into an official hydrological system.

The implemented GEE import boundary accepts only the documented sanitized observation schema and performs validation without database writes. Any column containing real identifiers, coordinates, levels, or volumes is rejected before row parsing.
