# Wildfire Smoke Impacts on Tallahassee: Analysis and Projections

## Project Overview

This project analyzes wildfire smoke impacts on Tallahassee, Florida, estimating historical effects and projecting future economic implications for state parks due to decreased attendance on high-smoke days. The analysis includes historical wildfire data, air quality measures, and behavioral survey responses to predict how smoke exposure might affect outdoor activities and park revenue.

The findings are intended to inform policymakers, city planners, and community stakeholders on potential mitigation strategies to address economic and social impacts of wildfire smoke.

---

## Repository Structure

### Overview
This represents the main structure of the repo. 
Each of these folders has it's own readme.md that provide more specific information about the files and notebooks found within.

- **Provided Resources**
    - Project and assignment instructions and provided code
- **Data Acquisition and Cleaning**
    - Scripts and data for retrieving and cleaning source datasets.
- **Data Analysis and Modeling**
    - Notebooks and intermediate outputs for smoke impact modeling.
- **Results and Presentation**
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

- **Behavioral Survey Data**: [Fowler et al., 2019 - Human Perception of and Response to Wildfire Smoke](https://www.nature.com/articles/s41597-019-0251-y)
  - Description: A dataset surveying 2,237 participants across the Boise Metropolitan Area in Idaho, including in-person and online responses. This dataset explores human behavior in response to wildfire smoke events, covering topics such as outdoor activity reduction, air quality awareness, health impacts, and effective communication strategies during smoke events. The data is publicly available under a [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).
  - The data can be downloaded [here](https://springernature.figshare.com/collections/A_Dataset_on_Human_Response_to_Wildfire_Smoke/4316795), but is also already downloaded and shared in this repo. 

- **Florida State Parks Data**: [Economic Impact Assessment Report, 2023](https://www.dep.state.fl.us/)
  - Description: The Florida State Parks Economic Impact Assessment (2022-2023) quantifies the economic contributions of state parks and greenways in Florida. The report includes detailed data on annual park attendance, visitor spending, state revenue from sales tax, and local job support. For example:
    - Annual attendance: Over 28.7 million visitors in FY 2022/2023.
    - Economic impact: $3.6 billion in direct economic contributions and over 50,427 jobs supported statewide.
    - Methodology: Uses models from the National Park Service and VISIT FLORIDA to estimate local economic benefits, including visitor expenditures on lodging, food, and transportation.
    - Accessibility: The data is available as part of the Florida Department of Environmental Protection's public records.

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
