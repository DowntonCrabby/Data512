# AQI Data Acquisition and Cleaning

## Overview

This folder contains scripts, notebooks, and intermediate data files used for retrieving, cleaning, and summarizing Air Quality Index (AQI) data for Tallahassee. The AQI data is used to assess the impact of wildfire smoke on air quality and its subsequent effect on outdoor activity and park attendance.

---

## Jupyter Notebooks and Python Files

### `Retrieve_AQI_Readings.ipynb`
- **Purpose**: 
  - Retrieves daily AQI readings for Tallahassee using the EPA Air Quality System (AQS) API.
  - Prepares the data by cleaning and transforming it into formats suitable for further analysis.
  - Generates intermediate files for both full-year and wildfire season AQI summaries.
- **Outputs**:
  - `AQI_annual_data.csv`: A summary of AQI data during wildfire season.
  - `AQI_fullYear_daily_avg.csv`: Daily AQI readings for the entire year.

---

## Intermediate Data Files

### `AQI_annual_data.csv`
- **Description**:
  - A yearly summary of AQI data focused only on the wildfire season.
  - Used for modeling the cumulative impact of wildfire smoke on air quality.
- **Columns**:
  1. **Year**: The calendar year of observation.
  2. **smoke_impact_sum**: Total smoke impact score for the wildfire season.
  3. **average_distance_miles**: Average distance of wildfires from Tallahassee (in miles).
  4. **fire_type_weight_mean**: Weighted average of fire types impacting air quality.
  5. **duration_days_sum**: Total number of days wildfires impacted AQI.
  6. **acres_sum**: Total acres burned during the wildfire season.
  7. **moderate_days**: Number of days with AQI classified as "Moderate."
  8. **unhealthy_days**: Number of days with AQI classified as "Unhealthy."
  9. **unhealthy_sens_days**: Number of days with AQI classified as "Unhealthy for Sensitive Groups."

### `AQI_fullYear_daily_avg.csv`
- **Description**:
  - Contains daily AQI readings for the entire year.
  - Provides a complete picture of air quality trends and seasonality.
- **Columns**:
  1. **date_local**: Date of the AQI reading (local timezone).
  2. **aqi**: Daily AQI value (numerical).

---

## Usage Notes

1. **Data Sources**:
   - AQI data is retrieved using the EPA Air Quality System (AQS) API. Ensure you have an active API key for running the `Retrieve_AQI_Readings.ipynb` notebook.

2. **Assumptions**:
   - `AQI_annual_data.csv` focuses only on wildfire season, defined based on historical wildfire activity in the region.
   - AQI values in `AQI_fullYear_daily_avg.csv` are averaged across all available monitoring stations for each day.

3. **Next Steps**:
   - These files are used in the `/Data Analysis and Modeling/` folder for impact modeling and visualization.

---

## Known Issues
- **Data Gaps**: AQI readings may be missing for some days due to monitoring station downtime or data unavailability.
- **Generalization**: AQI values are averaged across stations, which may not reflect localized variations in air quality.
