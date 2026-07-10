# Sentinel-2 Water Detection Methodology

## Sentinel-2 for Reservoir Monitoring

Sentinel-2 imagery can support reservoir monitoring by providing multispectral observations of reservoir surfaces during the flood period. In this MVP, Sentinel-2 is treated as a source for satellite-derived water area estimates, not as an official hydrological decision system. The workflow should record the observation date, source, ROI, cloud percentage, method version, and calculated water area.

## NDWI Water Mask

NDWI is a water index used to highlight water surfaces by comparing spectral bands where water and land often respond differently. In reservoir monitoring, NDWI can support water mask extraction inside a defined ROI. NDWI results can be affected by clouds, shadows, vegetation, mixed shoreline pixels, and threshold choices, so the result should be treated as a satellite-derived water area estimate.

## MNDWI Water Mask

MNDWI is a modified water index used for water surface detection. It can reduce confusion from some built-up or background surfaces compared with a simple water index in certain scenes. In this MVP, MNDWI area is stored as one estimate that can be compared with NDWI area and SCL water class area. Large differences between these methods should be flagged for analyst review.

## SCL Water Class

The Sentinel-2 Scene Classification Layer, or SCL, includes a water class that can be used as one source for water mask extraction. The SCL water class is useful for comparison, but it is not perfect ground truth. SCL results may be affected by cloud classification, shadows, snow or ice, shoreline mixed pixels, and processing limitations.
