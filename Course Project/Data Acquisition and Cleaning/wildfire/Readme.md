# Wildfire Data Cleaning and Distances Calculation
We are using the dataset to pull information on fires that are within 650 miles of  **Tallahassee, Florida**, over the most recent 60 years of wildfire data (1961-2021). We use the Combined Wildland Fire datasets provided by the US Geological Survey, supplemented by air quality data from the US EPA, to develop insights into the potential effects of wildfires on air quality.
## folder Structure
-**main folder/**: python files that do the data acquisition and/or data cleaning
- **created files/**: Folder containing the csvs that were created during the execution of the notebooks.

## Input Data Wildfire Data
The dataset was created by the USGS and is available on [ScienceBase](https://www.sciencebase.gov/catalog/item/61aa537dd34eb622f699df81).

The data files were too large to host on the github (as noted in the main readme)  but the following describes the files that were used for analysis and exploration:

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



## Data Cleaning Notebooks & .py Files
### Notebooks
- **Subset Wildfire Data and Calculate Distances.ipynb**: Jupyter notebook that subsets wildfire data and calculates distances from Tallahassee.

### modules
- **Geo_Calc.py**: Contains the geodetic distance calculation functions used to find fires within a specific radius of Tallahassee.
- **Wildfire_JSON_Reader.py**: Utility script for reading GeoJSON wildfire data.


## created files

This project produces several intermediate CSV files during the data retrieval, cleaning, and processing steps. Each file serves as a crucial input for further analysis and modeling. Below is a description of each file, its origin, and the columns it contains.


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

Code in this folder and based off oc examples provided by Dr. David W. McDonald for use in DATA 512, a course in the UW MS Data Science degree program. Dr. McDonald's code is provided under the Creative Commons CC-BY license. Revision 1.1 - August 16, 2024.

