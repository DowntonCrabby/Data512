# Wildfire Smoke Impact Analysis Project

## Project Overview

This repository is part of a course project focusing on the analysis of wildfire smoke impacts on US cities. The goal of the project is to estimate the annual impact of wildfire smoke on a specific city, understand the broader implications, and eventually inform policy makers on potential mitigation strategies. This project is conducted in multiple parts, with this repository documenting **Part 1 - Common Analysis**, where all students analyze wildfire impacts with a focus on individual cities assigned to them.

In Part 1, we estimate the annual wildfire smoke impact on our assigned city, **Tallahassee, Florida**, over the most recent 60 years of wildfire data (1961-2021). We use the Combined Wildland Fire datasets provided by the US Geological Survey, supplemented by air quality data from the US EPA, to develop insights into the potential effects of wildfires on air quality.

# Dataset Information

## Wildfire Data
This repository contains a subset of data and metadata files from a comprehensive geospatial dataset on wildland fires across the United States. The dataset was created by the USGS and is available on [ScienceBase](https://www.sciencebase.gov/catalog/item/61aa537dd34eb622f699df81).

These datasets were created by combining 40 different, published wildland fire data sources. Each data source varies in spatial scale, spatial resolution, and time period. The purpose of this combined dataset is to merge these disparate wildfire datasets, using a unified set of attributes, into a single set of polygons with a single fire boundary for each unique fire. This approach aims to provide a more comprehensive and consolidated fire dataset than any individual dataset, while reducing duplicate fire polygons and attributes.

The data files were too large to upload to this repo but the following describes the files that were used for analysis and exploration:
### Files

#### 1. `USGS_Wildland_Fire_Combined_Dataset.json`

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

#### 2. `combined_dataset.json.xml`

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

#### 3. `Wildland_Fire_Polygon_Metadata.xml`

This XML file provides additional metadata specific to the polygon fire perimeters within the combined dataset.

- **Structure**:
  - **`idinfo`**: Overview of the polygon dataset:
    - `citation`: Reference information, including title and publication date.
    - `descript`: Brief description of the dataset’s purpose and scope.
    - `spdom`: Spatial extent with geographic boundaries.
  - **`eainfo`**: Detailed description of individual attributes and field definitions within the polygon data, explaining the purpose of each field.
  - **`distinfo`**: Distribution information, including dataset format, availability, and access instructions.

# EPA AQI Data

# Repository Contents

- **Geo_Calc.py**: Contains the geodetic distance calculation functions used to find fires within a specific radius of Tallahassee.
- **Notebook1_Subset_Wildfire_Data_calculate_distances.ipynb**: Jupyter notebook that subsets wildfire data and calculates distances from Tallahassee.
- **Notebook2_Pull_AQI_Data.ipynb**: Notebook that pulls AQI data from the EPA AQS API for Tallahassee.
- **Notebook3_Smoke_Impact_Model.ipynb**: Notebook that develops a predictive model for estimating future wildfire smoke impacts for Tallahassee (for the years 2025-2050).
- **Notebook4_Data_Visualizations.ipynb**: Notebook containing visualizations related to the wildfire analysis, including time series graphs and histograms of fire data.
- **Reader.py**: Utility script for reading GeoJSON wildfire data.
- **Provided Resources/**: Folder containing additional resources provided for the course.
- **input files/**: Folder containing the input data files used for analysis.
## Intermediate Files

This project produces several intermediate CSV files during the data retrieval, cleaning, and processing steps. Each file serves as a crucial input for further analysis and modeling. Below is a description of each file, its origin, and the columns it contains.

### Files Produced by `Retrieve AQI Readings` Notebook

1. **all_aqi_data.csv**
   - **Description**: Contains raw AQI readings for all specified pollutants over the selected time period.
   - **Columns**:
     - `year`: The year the data was collected.
     - `date_local`: The local date of the AQI measurement.
     - `site_number`: Identifier for the monitoring site.
     - `latitude`, `longitude`: Geographical coordinates of the monitoring site.
     - `aqi`: The Air Quality Index (AQI) value.

2. **all_pollutant_data.csv**
   - **Description**: Includes data for various pollutants beyond AQI, capturing readings of particulate matter and gaseous pollutants.
   - **Columns**:
     - `year`, `date_local`, `site_number`, `latitude`, `longitude`: As described above.
     - `pollutant`: The type of pollutant measured (e.g., ozone, CO).
     - `value`: Concentration of the pollutant.
     - `units`: Units of measurement (e.g., ppm, µg/m³).

3. **subset_aqi_data.csv**
   - **Description**: A refined subset of `all_aqi_data.csv` that focuses on specific AQI values within a target date range or geographical area.
   - **Columns**:
     - `year`: Year of the AQI measurement.
     - `date_local`: The local date of the AQI measurement.
     - `site_number`: Monitoring site identifier.
     - `latitude`, `longitude`: Location of the monitoring site.
     - `aqi`: The AQI value for the measurement.

### Files Produced by `Subset Wildfire Data and Calculate Distances` Notebook

1. **fire_distances.csv**
   - **Description**: Contains data on wildfire incidents and calculates the distance of each fire from the specified city or region of interest. Each entry represents a unique wildfire event.
   - **Columns**:
     - `usgs_assigned_id`: Unique identifier for each wildfire event.
     - `fire_year`: The year of the fire.
     - `fire_dates`: Date range during which the fire burned.
     - `fire_name`: Name of the wildfire.
     - `fire_size_acres`: Size of the fire in acres.
     - `fire_type`: Classification of the fire (e.g., Wildfire, Prescribed Burn).
     - `closest_distance_miles`: Closest distance from the fire to the city (in miles).
     - `closest_point_lat`, `closest_point_lon`: Coordinates of the closest point on the wildfire perimeter.
     - `average_distance_miles`: Average distance from the wildfire to the city.

2. **Wildland_Fire_Combined_Subset.csv**
   - **Description**: A combined dataset of wildfire data specific to the target city or area, filtered to include essential attributes for the analysis.
   - **Columns**:
     - `USGS_Assigned_ID`: Unique identifier for each wildfire.
     - `Assigned_Fire_Type`: Classification of the fire (e.g., Wildfire, Prescribed Burn).
     - `Fire_Year`: The year of the wildfire.
     - `Trusted_Start_Date`: Estimated start date of the fire.
     - `Trusted_End_Date`: Estimated end date of the fire.
     - `duration_days`: Total duration of the fire (in days).
     - `GIS_Acres`: Geographic Information System-calculated acres burned.

These intermediate files provide structured data essential for further analysis, including examining air quality impacts of wildfires, calculating smoke exposure levels, and identifying trends over time.

## Methodology

The analysis follows several key steps:

1. **Data Acquisition**: Load the Combined Wildland Fire dataset and the EPA AQS air quality data.
2. **Data Processing**: Filter the dataset to include only fires within 650 miles of Tallahassee. Calculate geodetic distances and determine the annual smoke impact estimates.
3. **Smoke Impact Estimation**: Estimate the annual wildfire smoke impact for each year from 1961 to 2021. The estimate considers factors such as fire size and proximity to the city.
4. **AQI Comparison**: Compare the wildfire smoke estimates to the EPA AQI data for Tallahassee to assess the accuracy of our estimates.
5. **Predictive Modeling**: Develop a predictive model to estimate wildfire smoke impacts for the next 25 years (2025-2050).
6. **Visualization**: Create time series graphs and histograms to visualize the findings of the analysis.

## Licensing and Use

This project is licensed under the MIT License. See the LICENSE file for more details.

The wildfire data is publicly available on [ScienceBase](https://www.sciencebase.gov/catalog/item/61aa537dd34eb622f699df81). For licensing information, please refer to the original publication page for any specific usage restrictions or licensing notes.



## Acknowledgments

This project was completed as part of a course assignment. Special thanks to the US Geological Survey and US EPA for providing the datasets used in this analysis. 

Code in this repo developed and based off oc examples provided by Dr. David W. McDonald for use in DATA 512, a course in the UW MS Data Science degree program. Dr. McDonald's code is provided under the Creative Commons CC-BY license. Revision 1.1 - August 16, 2024.

