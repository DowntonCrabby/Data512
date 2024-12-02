# Source Data Acquisition and Documentation

## Overview

This repository contains a subset of data and metadata files from a comprehensive geospatial dataset on wildland fires across the United States. The dataset was created by the USGS and is available on [ScienceBase](https://www.sciencebase.gov/catalog/item/61aa537dd34eb622f699df81).

These datasets were created by combining 40 different, published wildland fire data sources. Each data source varies in spatial scale, spatial resolution, and time period. The purpose of this combined dataset is to merge these disparate wildfire datasets, using a unified set of attributes, into a single set of polygons with a single fire boundary for each unique fire. This approach aims to provide a more comprehensive and consolidated fire dataset than any individual dataset, while reducing duplicate fire polygons and attributes.

## Files

### 1. `USGS_Wildland_Fire_Combined_Dataset.json`

This JSON file contains geospatial data on individual wildland fire events. Each fire event is represented as a "feature" with detailed properties and geometry information for spatial analysis.

- **Structure**:
  - **`type`**: Specifies the type of data structure (typically "FeatureCollection").
  - **`features`**: Array containing individual fire events with the following fields:
    - **`type`**: Type of feature, usually "Feature."
    - **`attributes`**: Metadata about each fire event:
      - `OBJECTID`: Unique identifier for the fire event.
      - `USGS_Assigned_ID`: Internal USGS identifier.
      - `Assigned_Fire_Type`: Type of fire (e.g., Wildfire).
      - `Fire_Year`: Year the fire occurred.
      - `GIS_Acres`: Estimated acres burned.
      - `Source_Datasets`: Source datasets used to map the fire perimeter.
      - Additional fields including fire name, cause, codes, notes, and digitizing methods.
    - **`geometry`**: Geospatial data indicating the fire perimeter, with:
      - `type`: Generally "Polygon" or "MultiPolygon" to represent the fire boundary.
      - `rings`: Array of coordinate points forming the perimeter(s) of the fire event.

### 2. `combined_dataset.json.xml`

This XML file contains metadata describing the `USGS_Wildland_Fire_Combined_Dataset.json` file, outlining its creation, sources, and quality.

- **Structure**:
  - **`idinfo`**: General information about the dataset:
    - `citation`: Publication title, publication date, authors, and access links.
    - `descript`: Detailed abstract, purpose, and dataset limitations.
    - `timeperd`: Temporal range (1835–2020) and the currentness of the data.
    - `status`: Dataset progress and frequency of updates.
    - `spdom`: Spatial domain, including the geographic bounds of the dataset.
  - **`dataqual`**: Data quality information:
    - `attracc`: Attribute accuracy and any known limitations.
    - `logic`: Logical consistency details.
    - `complete`: Information on dataset completeness and any assumed gaps.
    - `posacc`: Positional accuracy.
    - `lineage`: Information on the source datasets used to compile this combined dataset, including the process steps and methods.
  - **`srcinfo`**: Source datasets ranked by quality tiers (1–8). The highest-quality source data was used to represent each fire perimeter.

### 3. `Wildland_Fire_Polygon_Metadata.xml`

This XML file provides additional metadata specific to the polygon fire perimeters within the combined dataset.

- **Structure**:
  - **`idinfo`**: Overview of the polygon dataset:
    - `citation`: Reference information, including title and publication date.
    - `descript`: Brief description of the dataset’s purpose and scope.
    - `spdom`: Spatial extent with geographic boundaries.
  - **`eainfo`**: Detailed description of individual attributes and field definitions within the polygon data, explaining the purpose of each field.
  - **`distinfo`**: Distribution information, including dataset format, availability, and access instructions.

## Licensing and Use

The data is publicly available on [ScienceBase](https://www.sciencebase.gov/catalog/item/61aa537dd34eb622f699df81). For licensing information, please refer to the original publication page for any specific usage restrictions or licensing notes.
---

This documentation provides a comprehensive overview of the subset files and their structures, assisting users in understanding and utilizing the wildland fire dataset for geospatial and analytical purposes.

