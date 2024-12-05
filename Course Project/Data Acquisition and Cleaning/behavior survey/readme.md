# Behavioral Survey on Responses to Wildfire Smoke
The behavioral data analyzed in this folder originates from a study conducted by researchers at Boise State University and collaborators. This study explored how people perceive and respond to wildfire smoke, focusing on the Boise Metropolitan Area in Idaho. 

The survey included a wide range of topics, such as:
- Demographic information (e.g., age, gender, education level, income).
- Outdoor activity engagement and adjustments due to smoke exposure.
- Sources and frequency of air quality notifications.
- Perceptions of wildfire smoke as a hazard compared to other natural disasters.
- Smoke-related health experiences and mitigation strategies.

## Repository Structure

- **input_data/**: Contains survey datasets and associated metadata.
- **created_files/**: Contains processed data files and analysis results.


## Input Data

### Datasets

1. **Online Survey Data**  
   File: `Online Table.csv`  
   Description: Contains survey responses collected from 1,623 participants via an online questionnaire distributed to Boise State University students, faculty, and staff.

2. **In-Person Survey Data**  
   File: `Inperson Table.csv`  
   Description: Contains survey responses from 614 individuals who participated in the study across various public locations in the Boise Metropolitan Area.

3. **Metadata**  
   - `metadata.txt`: A summary of the dataset's background, including the study's goals, methodology, and participant demographics.  
   - `metadata.xml`: Structured XML metadata providing detailed descriptions of survey questions, response options, and survey logistics.

---

## Scripts

1. **`survey_parser.py`**  
   A Python script for parsing, cleaning, and structuring survey data. Key functionalities include:
   - Mapping raw survey question identifiers to human-readable labels.
   - Handling multi-level headers in the survey data CSV files.
   - Splitting and processing data by survey question.

2. **`load_with_SP.ipynb`**  
   A Jupyter notebook demonstrating how to load and process survey data using the functions defined in `survey_parser.py`. It serves as an example pipeline for cleaning and preparing the survey data for analysis.



