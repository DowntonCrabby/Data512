# Wildfire Smoke Impacts on Tallahassee: Analysis and Projections

## Project Overview

This project analyzes wildfire smoke impacts on Tallahassee, Florida, estimating historical effects and projecting future economic implications for state parks due to decreased attendance on high-smoke days. The analysis includes historical wildfire data, air quality measures, and behavioral survey responses to predict how smoke exposure might affect outdoor activities and park revenue.

The findings are intended to inform policymakers, city planners, and community stakeholders on potential mitigation strategies to address economic and social impacts of wildfire smoke.

---

## Repository Structure

### Overview
This represents the main structure of the repo. 
Each of these folders has it's own readme.md that provide more specific information about the files and notebooks found within.

**Provided Resources**
    - Project and assignment instructions and provided code
**Data Acquisition and Cleaning**
    - Scripts and data for retrieving and cleaning source datasets.
**Data Analysis and Modeling**
    - Notebooks and intermediate outputs for smoke impact modeling.
**Results and Presentation**
    - Final results, visualizations, and project presentations.


## Data Sources
This project uses the following data sources:
- **Wildfire Dataset**: [USGS Wildland Fire Combined Dataset](https://www.sciencebase.gov/catalog/item/61aa537dd34eb622f699df81)
  - Description: A comprehensive geospatial dataset combining 40 published wildland fire data sources.
  - This dataset is too large to share via this github so to work with this data you will need to go to the link and download the data
      - This analysis utilized the following files from that dataset:
      - `USGS_Wildland_Fire_Combined_Dataset.json`
      - `USGS_Wildland_Fire_Combined_Dataset.csv`
      - `usgs_wildland_fire_combined_dataset.json.xml`
      - `Wildland_Fire_Polygon_Metadata.xml`
- **AQI Data**: EPA Air Quality System API ([AirNow](https://www.airnow.gov/))
  - Description: Air Quality Index data for historical and current pollution levels.
    
- **Behavioral Survey Data**: [Survey Dataset](link-placeholder)
  - Description: Self-reported activity changes in response to air quality conditions.

- **Florida State Parks Data**:
  - Description: Park attendance and revenue data for analyzing economic impacts.

 ## Instructions to Run

Follow these steps to replicate the analysis:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/wildfire-smoke-impact.git
   cd wildfire-smoke-impact
   ```

2. **Set Up the Environment:** Install required dependencies using the `requirements.txt` file
   - ` pip install -r requirements.txt`

3. **Manually Download Fire Data:** Download the [USGS Wildland Fire Combined Dataset](https://www.sciencebase.gov/catalog/item/61aa537dd34eb622f699df81)

4. **Run Data Acquisition Notebooks**: Navigate to `/Data Acquisition and Cleaning/`
   - Example: Retrieve AQI data:
    ` jupyter notebook aqi/Retrieve_AQI_Readings.ipynb`
  
5. **Run Analysis Notebooks:** Navigate to `/Data Analysis and Modeling/` and execute analysis notebooks.
    - Example: Build the smoke impact model:
   `jupyter notebook Fire_Smoke_Model.ipynb`

6. **View Results:** Generated outputs, visualizations, and final results and presentation are located in `/Results and Presentation/`


---

### **Known Issues**

- **Survey Data Generalization**:
  The behavioral survey data was collected in Boise, Idaho. While assumptions are made to apply this data to Tallahassee, differences in climate, wildfire exposure, and population behavior may affect accuracy.

- **AQI Data Gaps**:
  AQI data availability varies across years, with some gaps in historical data for certain locations.

- **Model Assumptions**:
  The predictive model assumes linear relationships between smoke impacts and attendance reductions, which may oversimplify complex human behaviors.

- **Data Licensing**:
  The terms of use for public datasets must be followed. Refer to the respective sources for specific restrictions.


## Licensing and Use

This project is licensed under the MIT License. For details, see the `MIT License.md` file. All datasets used are publicly available, with attribution to their respective providers:
- USGS Wildland Fire Combined Dataset ([ScienceBase](https://www.sciencebase.gov/catalog/item/61aa537dd34eb622f699df81)).
- EPA Air Quality System API ([AirNow](https://www.airnow.gov/)).
- Survey and park data from respective sources.

## Acknowledgments

Special thanks to:
- The US Geological Survey and EPA for providing essential datasets.
- Course instructors and collaborators for guidance and resources.
- Dr. David W. McDonald for code examples used as a foundation for this project, provided under the Creative Commons CC-BY license.
