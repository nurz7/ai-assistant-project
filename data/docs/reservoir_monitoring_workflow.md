# Reservoir Monitoring Workflow

## ROI and Water Mask Extraction

ROI means region of interest. For reservoir monitoring, the ROI should cover the reservoir while avoiding unrelated land, neighboring water bodies, and unnecessary background area. A water mask marks pixels treated as water inside the ROI. The quality of the ROI affects the final satellite-derived water area calculation.

## Cloud Filtering

Cloud filtering is required because clouds, cloud shadows, haze, and snow can distort water detection. Observations with high cloud percentage should be flagged as low confidence or excluded from strong conclusions. The assistant should mention cloud percentage when explaining an observation or monitoring report.

## Area Calculation

Satellite-derived water area can be estimated by counting water pixels inside the ROI and converting the pixel count into square kilometers. The calculation should identify which method produced the water mask, such as SCL water class, MNDWI, or NDWI. Results should include units, method version, ROI area, and limitations.

## Method Version and Limitations

Each observation should record a method version so analysts can compare results consistently over time. Limitations should mention cloud filtering, ROI quality, threshold choices, shoreline mixed pixels, and disagreement between SCL, NDWI, and MNDWI estimates. The assistant should not present a single method result as unquestionable ground truth.
