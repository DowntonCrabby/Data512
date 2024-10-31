##################
# IMPORTS
##################

import json
import time
import requests
from typing import Any, Dict, List, Optional
import pandas as pd

##################
# CONSTANTS
##################

API_REQUEST_URL = 'https://aqs.epa.gov/data/api'
API_THROTTLE_WAIT = 0.1  # Throttle wait time between requests
EMAIL = 'kateroll@gmail.com'
API_KEY = 'silverfox66'

AQI_PARAMS_GASEOUS = ["O3", "NO2", "SO2"]
AQI_PARAMS_PARTICULATES = ["PM2.5", "PM10"]
EXTRACTION_FIELDS = ['sample_duration', 'observation_count', 'arithmetic_mean', 'aqi']

# API Endpoints
API_ACTION_LIST_CLASSES = '/list/classes?email={email}&key={key}'
API_ACTION_LIST_PARAMS = '/list/parametersByClass?email={email}&key={key}&pc={pclass}'
API_ACTION_MONITORS_COUNTY = '/monitors/byCounty?email={email}&key={key}&param={param}&bdate={begin_date}&edate={end_date}'
API_ACTION_MONITORS_BOX = '/monitors/byBox?email={email}&key={key}&param={param}&minlat={minlat}&maxlat={maxlat}&minlon={minlon}&maxlon={maxlon}&bdate={begin_date}&edate={end_date}'
API_ACTION_DAILY_SUMMARY_COUNTY = '/dailyData/byCounty?email={email}&key={key}&param={param}&state={state}&county={county}&bdate={begin_date}&edate={end_date}'

AQS_REQUEST_TEMPLATE = {
    "email":      "kateroll@gmail.com",     
    "key":        "silverfox66",      
    "state":      "12",     # the two digit state FIPS # as a string
    "county":     "073",     # the three digit county FIPS # as a string
    "begin_date": "",     # the start of a time window in YYYYMMDD format
    "end_date":   "",     # the end of a time window in YYYYMMDD format, begin_date and end_date must be in the same year
    "minlat":    29.71366231884058,
    "maxlat":    31.162937681159423,
    "minlon":    -85.19645091575092,
    "maxlon":    -83.36494908424908,
    "param":     "",     # a list of comma separated 5 digit codes, max 5 codes requested
    "pclass":    ""      # parameter class is only used by the List calls
}

##################
# GENERAL API FUNCTIONS
##################

def calculate_bounding_box(lat: float, lon: float, scale: float = 1.0) -> Dict[str, float]:
    """
    Calculate a bounding box around a given latitude and longitude.

    Parameters
    ----------
    lat : float
        Latitude of the center point.
    lon : float
        Longitude of the center point.
    scale : float, optional
        Scale factor to adjust the bounding box size, default is 1.0.

    Returns
    -------
    dict
        Bounding box coordinates with min and max latitude and longitude.
    """
    lat_25_miles = 25.0 * (1.0 / 69.0)
    lon_25_miles = 25.0 * (1.0 / 54.6)
    return {
        "min_lat": lat - scale * lat_25_miles,
        "max_lat": lat + scale * lat_25_miles,
        "min_lon": lon - scale * lon_25_miles,
        "max_lon": lon + scale * lon_25_miles
    }


def make_api_request(url: str, headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
    """
    Makes a request to the given URL, handling any errors and returning the
    JSON response as a dictionary.

    Parameters
    ----------
    url : str
        The URL to request.
    headers : dict, optional
        Headers for the request, if any.

    Returns
    -------
    dict or None
        JSON response as a dictionary, or None if an error occurs.
    """
    try:
        if API_THROTTLE_WAIT > 0:
            time.sleep(API_THROTTLE_WAIT)
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

##################
# REQUESTING MONITORS
##################

def request_monitors(bounding_box: Optional[Dict[str, float]] = None,
                     param: Optional[str] = None,
                     begin_date: str = "20210701",
                     end_date: str = "20210731",
                     email: str = EMAIL,
                     api_key: str = API_KEY,
                     endpoint_action: str = API_ACTION_MONITORS_BOX) -> pd.DataFrame:
    """
    Requests monitoring stations within a bounding box or by county.

    Parameters
    ----------
    bounding_box : dict, optional
        Bounding box with min and max latitude and longitude.
    param : str, optional
        AQI parameter to request.
    begin_date : str
        Start date for data retrieval in YYYYMMDD format.
    end_date : str
        End date for data retrieval in YYYYMMDD format.
    email : str
        Email for API authentication.
    api_key : str
        API key for authentication.
    endpoint_action : str
        API action endpoint for bounding box requests.

    Returns
    -------
    pd.DataFrame
        DataFrame of monitoring station data, or empty DataFrame if no data.
    """
    request_params = {
        'email': email,
        'key': api_key,
        'param': param,
        'begin_date': begin_date,
        'end_date': end_date,
    }

    if bounding_box:
        request_params.update(bounding_box)

    request_url = API_REQUEST_URL + endpoint_action.format(**request_params)
    response = make_api_request(request_url)

    # Convert response to DataFrame if successful
    if response and "Data" in response:
        return pd.DataFrame(response["Data"])
    return pd.DataFrame()  # Return empty DataFrame if no data


def request_monitors_B(bounding_box: Optional[Dict[str, float]] = None,
                     param: Optional[str] = None,
                     begin_date: str = "20210701",
                     end_date: str = "20210731",
                     email: str = EMAIL,
                     api_key: str = API_KEY,
                     endpoint_action: str = API_ACTION_MONITORS_BOX) -> pd.DataFrame:
    """
    Requests monitoring stations within a bounding box or by county.

    Parameters
    ----------
    bounding_box : dict, optional
        Bounding box with min and max latitude and longitude.
    param : str, optional
        AQI parameter to request.
    begin_date : str
        Start date for data retrieval in YYYYMMDD format.
    end_date : str
        End date for data retrieval in YYYYMMDD format.
    email : str
        Email for API authentication.
    api_key : str
        API key for authentication.
    endpoint_action : str
        API action endpoint for bounding box requests.

    Returns
    -------
    pd.DataFrame
        DataFrame of monitoring station data, or empty DataFrame if no data.
    """
    # Copy template to ensure we have all required fields
    request_params = AQS_REQUEST_TEMPLATE.copy()
    request_params.update({
        'email': email,
        'key': api_key,
        'param': param,
        'begin_date': begin_date,
        'end_date': end_date
    })

    if bounding_box:
        request_params.update({
            'minlat': bounding_box['minlat'],
            'maxlat': bounding_box['maxlat'],
            'minlon': bounding_box['minlon'],
            'maxlon': bounding_box['maxlon']
        })

    request_url = API_REQUEST_URL + endpoint_action.format(**request_params)
    response = make_api_request(request_url)

    # Convert response to DataFrame if successful
    if response and "Data" in response:
        return pd.DataFrame(response["Data"])
    return pd.DataFrame()  # Return empty DataFrame if no data
##################
# REQUESTING READINGS
##################

def fetch_aqi_readings(station_id: str,
                       start_date: str,
                       end_date: str,
                       params: List[str],
                       email: str = EMAIL,
                       api_key: str = API_KEY) -> pd.DataFrame:
    """
    Fetch AQI readings for a specific station and date range.

    Parameters
    ----------
    station_id : str
        The station identifier.
    start_date : str
        Start date in YYYYMMDD format.
    end_date : str
        End date in YYYYMMDD format.
    params : list of str
        List of AQI parameters (e.g., AQI_PARAMS_GASEOUS or AQI_PARAMS_PARTICULATES).
    email : str
        Email for API authentication.
    api_key : str
        API key for authentication.

    Returns
    -------
    pd.DataFrame
        DataFrame containing AQI readings for the station and date range.
    """
    request_params = {
        'email': email,
        'key': api_key,
        'station_id': station_id,
        'start_date': start_date,
        'end_date': end_date,
        'parameters': ','.join(params)
    }
    request_url = API_REQUEST_URL + "/dailyData/byStation?" + "&".join(f"{k}={v}" for k, v in request_params.items())
    response = make_api_request(request_url)

    # Return as DataFrame
    if response and "Data" in response:
        return pd.DataFrame(response["Data"])
    return pd.DataFrame()  # Return empty DataFrame if no data

##################
# DATA EXTRACTION AND SUMMARY
##################

def extract_summary_from_response(response: Dict[str, Any], fields: List[str] = EXTRACTION_FIELDS) -> pd.DataFrame:
    """
    Extracts a summary of specified fields from each record in the response,
    organized by monitoring site, parameter, and date.

    Parameters
    ----------
    response : dict
        API response data.
    fields : list of str, optional
        List of fields to extract from each record.

    Returns
    -------
    pd.DataFrame
        DataFrame summarizing extracted data by site, parameter, and date.
    """
    records = []
    for record in response.get("Data", []):
        record_data = {
            "site_id": record.get('site_number'),
            "local_site_name": record.get('local_site_name'),
            "state": record.get('state'),
            "county": record.get('county'),
            "date": record.get('date_local').replace('-', ''),
            "parameter_code": record.get('parameter_code'),
            "parameter_name": record.get('parameter'),
            "units_of_measure": record.get('units_of_measure')
        }

        for field in fields:
            record_data[field] = record.get(field, None)
        
        records.append(record_data)

    return pd.DataFrame(records)
