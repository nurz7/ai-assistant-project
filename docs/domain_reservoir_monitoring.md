# Domain: Reservoir Monitoring

## Domain Overview

Reservoir monitoring is the process of observing water bodies over time to understand changes in water area, water level, storage, and potential risk conditions. For small reservoirs, especially during the flood period, monitoring can help analysts notice rapid changes, missing observations, or suspicious differences between expected and observed conditions.

This project focuses on a practical AI/GIS workflow around satellite-derived water area and structured reservoir observations. It does not attempt to replace hydrological modeling or official monitoring systems.

## Why Reservoir Monitoring Matters

Reservoir monitoring can support:

- flood-season situational awareness;
- infrastructure monitoring;
- comparison of observed water extent with reference values;
- early review of suspicious observations;
- reporting for analysts and managers;
- prioritization of reservoirs that need closer expert review.

For small reservoirs, consistent monitoring can be difficult because observations may be fragmented across satellite data, local records, passport/reference values, spreadsheets, and reports. A focused AI assistant can help organize this information and explain methodology limitations.

## What Data Is Used

The MVP should use only synthetic or public-safe data.

Possible data categories:

- methodology/SOP documents;
- reservoir profile data;
- passport area;
- normal level;
- dead level;
- coordinates;
- satellite observation dates;
- Sentinel-2 derived water area estimates;
- NDWI area;
- MNDWI area;
- SCL water class area;
- cloud percentage;
- ROI area;
- method version;
- optional area-level reference records.

Private, confidential, or unpublished datasets must not be presented as included in this repository.

## Sentinel-2 at a High Level

Sentinel-2 is a satellite mission commonly used for land and water observation. Its multispectral imagery can support water surface detection because different surface types reflect light differently across spectral bands.

In this project, Sentinel-2 is treated as a source for satellite-derived water area estimates. The MVP does not need to process raw satellite imagery directly. It can start from synthetic or exported observation values.

## NDWI at a High Level

NDWI stands for Normalized Difference Water Index.

At a high level, NDWI is used to highlight water surfaces by comparing spectral bands where water and land tend to behave differently. In a reservoir-monitoring workflow, NDWI can help estimate a water mask and calculate satellite-derived water area.

NDWI results can be affected by clouds, shadows, vegetation, mixed pixels, shoreline complexity, and threshold choices.

## MNDWI at a High Level

MNDWI stands for Modified Normalized Difference Water Index.

At a high level, MNDWI is another water index often used to improve water surface extraction in some environments, especially where built-up areas or background surfaces can confuse basic water detection.

In this project, MNDWI is one of several water area estimates that can be compared with NDWI and SCL water class outputs.

## SCL Water Class at a High Level

SCL means Scene Classification Layer in Sentinel-2 processing products.

The SCL water class can identify pixels classified as water by the processing algorithm. It can be useful as one method for estimating water area, but it should not be treated as perfect ground truth.

SCL results may be affected by cloud classification, shadows, snow/ice, shoreline mixed pixels, and processing limitations.

## ROI and Water Mask

ROI means region of interest.

For reservoir monitoring, an ROI defines the area where water extraction is evaluated. A good ROI should cover the reservoir and avoid too much unrelated land or neighboring water bodies.

A water mask is a pixel-level classification or thresholded layer that marks which pixels are treated as water. Water area can be estimated by counting water pixels within the ROI and converting pixel count to area.

## How Water Area Can Be Estimated

A simplified workflow:

1. Select reservoir ROI.
2. Select satellite observation date.
3. Apply cloud filtering or reject observations with too much cloud cover.
4. Generate a water mask using NDWI, MNDWI, SCL water class, or another method.
5. Calculate water pixels inside the ROI.
6. Convert pixel count to area.
7. Compare satellite-derived water area with passport/reference area.
8. Record method version and limitations.

The MVP can demonstrate this workflow using synthetic or exported observation values instead of processing raw rasters.

## Why Cloud Filtering Matters

Clouds, cloud shadows, haze, and snow can distort water detection. High cloud percentage may make an observation unreliable or unusable.

The assistant should flag observations with high cloud percentage and avoid strong conclusions from low-quality imagery.

## Passport Area

Passport area is a reference area value recorded for a reservoir, often from documentation or engineering records.

In this project, passport area is used as a reference for comparison with satellite-derived water area. It should not be treated as a dynamic measurement for every observation date.

Large differences between observed area and passport area may indicate a real change, a seasonal condition, an extraction issue, cloud contamination, ROI problem, or data error.

## Normal Level and Dead Level

Normal level is a reference water level associated with normal reservoir operation or design conditions.

Dead level is a lower reference level below which useful storage or water release may be limited, depending on reservoir design and documentation.

These terms are important for hydrological interpretation, but the assistant must not infer exact water level from area alone unless validated area-level relationship data is available.

## Area-Level Relationship

An area-level relationship links water surface area to water level, usually through validated reservoir geometry, survey data, curves, or reliable reference measurements.

Without a validated area-level relationship, satellite-derived water area can support comparison and anomaly flagging, but it cannot safely produce exact water level.

## What the Assistant Can Conclude

The assistant can:

- explain methodology from retrieved documents;
- cite sources;
- show reservoir profile information from synthetic/demo data;
- show satellite-derived water area observations;
- compare observed water area with passport/reference area;
- flag high cloud percentage;
- flag conflicting NDWI, MNDWI, and SCL estimates;
- flag missing observations;
- generate short monitoring reports with limitations.

## What the Assistant Cannot Conclude

The assistant cannot:

- make official hydrological decisions;
- certify reservoir safety;
- claim exact water level without validated data;
- replace expert review;
- use private or confidential datasets;
- connect to real government systems in the MVP;
- perform final operational actions automatically.

## Connection to the Master's Research Topic

The owner's master's research topic is:

```text
Development of methods for calculating water levels of small reservoirs in Kazakhstan during the flood period.
```

This project connects to that topic by focusing on the AI/data workflow around reservoir monitoring:

- explaining methodology;
- organizing observations;
- comparing satellite-derived water area with reference values;
- identifying data quality issues;
- documenting limitations;
- preparing analyst-friendly monitoring reports.

The repository should not present itself as the complete thesis or as a validated scientific water-level model. It should present itself as a practical AI implementation prototype related to the broader research domain.

## Connection to AI Implementation Jobs

This domain is useful for job applications because it shows:

- LLM integration in a real workflow;
- RAG over methodology documents;
- structured data lookup;
- simple calculations and anomaly checks;
- FastAPI backend design;
- Streamlit demo UI;
- evaluation and safety thinking;
- domain-specific product framing;
- ability to translate research context into an applied AI prototype.

That makes the project relevant for AI Engineer, AI Specialist, AI Solutions Developer, GIS AI, and data workflow roles.
