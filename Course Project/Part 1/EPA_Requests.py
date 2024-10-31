
##################
#    IMPORTS
###################

import json
import time
import requests
import pandas as pd
from typing import Any, Dict, List, Optional, Union

##################
#    API CONSTANTS
###################

#################
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
API_ACTION_LIST_SITES = '/list/sitesByCounty?email={email}&key={key}&state={state}&county={county}'
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
# GENERAL API UTILITIES
###################

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


##################
# REQUESTING MONITORS
###################

def request_monitors(email_address: Optional[str] = EMAIL,
                     key: Optional[str] = API_KEY,
                     param: Optional[str] = None,
                     begin_date: Optional[str] = None,
                     end_date: Optional[str] = None,
                     fips: Optional[str] = None,
                     minlat: Optional[float] = None,
                     maxlat: Optional[float] = None,
                     minlon: Optional[float] = None,
                     maxlon: Optional[float] = None,
                     endpoint_url: str = API_REQUEST_URL,
                     endpoint_action: str = '/monitors/byCounty',
                     request_template: Dict[str, Any] = AQS_REQUEST_TEMPLATE,
                     headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
    """
    Requests monitoring stations information from the API, with options for filtering by state, county, or bounding box.
    Parameters
    ----------
    email_address : str, optional
        User email address for API access. Default is EMAIL.
    key : str, optional
        API key for authentication. Default is API_KEY.
    param : str, optional
        Parameter code to request specific measurements. Default is None.
    begin_date : str, optional
        Start date for data retrieval (YYYYMMDD format). Default is None.
    end_date : str, optional
        End date for data retrieval (YYYYMMDD format). Default is None.
    fips : str, optional
        FIPS code for the state and county. Default is None.
    minlat, maxlat, minlon, maxlon : float, optional
        Bounding box coordinates. Defaults are None.
    endpoint_url : str, optional
        Base URL for the API endpoint. Default is API_REQUEST_URL.
    endpoint_action : str, optional
        Action to specify in API call. Default is '/monitors/byCounty'.
    request_template : dict, optional
        Template for API request parameters. Default is AQS_REQUEST_TEMPLATE.
    headers : dict, optional
        Headers for the API request. Default is None.
    Returns
    -------
    dict or None
        JSON response from the API if successful, otherwise None.
    """
    request_template = request_template.copy()
    request_template.update({
        'email': email_address,
        'key': key,
        'param': param,
        'begin_date': begin_date,
        'end_date': end_date,
    })

    if minlat is not None and maxlat is not None and minlon is not None and maxlon is not None:
        request_template.update({
            'minlat': minlat,
            'maxlat': maxlat,
            'minlon': minlon,
            'maxlon': maxlon
        })
    elif fips:
        request_template['state'] = fips[:2]
        request_template['county'] = fips[2:]

    required_keys = ['email', 'key', 'param', 'begin_date', 'end_date']
    if not all(request_template.get(key) for key in required_keys):
        raise ValueError("Must supply email, key, param, begin_date, and end_date for 'request_monitors'")

    request_url = endpoint_url + endpoint_action.format(**request_template)
    try:
        if API_THROTTLE_WAIT > 0.0:
            time.sleep(API_THROTTLE_WAIT)
        response = requests.get(request_url, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


def get_monitors_in_bounding_box(bounding_box: List[float],
                                 param: List[str] = AQI_PARAMS_PARTICULATES,
                                 begin_date: str = "20210701",
                                 end_date: str = "20210731",
                                 email_address: str = EMAIL,
                                 api_key: str = API_KEY,
                                 endpoint_action: str = '/monitors/byBox') -> Optional[Dict[str, Any]]:
    """
    Retrieves monitoring station data within a specified bounding box.
    Parameters
    ----------
    bounding_box : list of float
        List containing min_lat, max_lat, min_lon, max_lon of the bounding box.
    param : list of str, optional
        List of AQI parameters to filter by (e.g., AQI_PARAMS_PARTICULATES). Default is AQI_PARAMS_PARTICULATES.
    begin_date : str, optional
        Start date for data retrieval in YYYYMMDD format. Default is "20210701".
    end_date : str, optional
        End date for data retrieval in YYYYMMDD format. Default is "20210731".
    email_address : str, optional
        User email address for API access. Default is EMAIL.
    api_key : str, optional
        API key for authentication. Default is API_KEY.
    endpoint_action : str, optional
        API action for bounding box requests. Default is '/monitors/byBox'.
    Returns
    -------
    dict or None
        JSON response from the API if successful, otherwise None.
    """
    request_data = AQS_REQUEST_TEMPLATE.copy()
    request_data.update({
        'email': email_address,
        'key': api_key,
        'param': param,
        'begin_date': begin_date,
        'end_date': end_date,
        'minlat': bounding_box[0],
        'maxlat': bounding_box[1],
        'minlon': bounding_box[2],
        'maxlon': bounding_box[3],
    })

    response = request_monitors(request_template=request_data, endpoint_action=endpoint_action)
    if response and response.get("Header", [{}])[0].get('status') == "Success":
        print(json.dumps(response['Data'], indent=4))
        return response['Data']
    else:
        print("Error in response:", json.dumps(response, indent=4))
        return None


##################
# REQUESTING READINGS
###################

def request_daily_summary(email_address: Optional[str] = None,
                          key: Optional[str] = None,
                          param: Optional[str] = None,
                          begin_date: Optional[str] = None,
                          end_date: Optional[str] = None,
                          fips: Optional[str] = None,
                          endpoint_url: str = API_REQUEST_URL,
                          endpoint_action: str = API_ACTION_DAILY_SUMMARY_COUNTY,
                          request_template: Dict[str, Any] = AQS_REQUEST_TEMPLATE,
                          headers: Optional[Dict[str, str]] = None,
                          fields: List[str] = EXTRACTION_FIELDS) -> pd.DataFrame:
    """
    Requests and extracts a daily summary of air quality data for a specific county and time period.

    Parameters
    ----------
    email_address : str, optional
        User's email address for API authentication; overrides template value if provided.
    key : str, optional
        API key for authentication; overrides template value if provided.
    param : str, optional
        AQI parameter code(s) for the request.
    begin_date : str, optional
        Start date for data retrieval in YYYYMMDD format.
    end_date : str, optional
        End date for data retrieval in YYYYMMDD format.
    fips : str, optional
        FIPS code of the location (state and county).
    endpoint_url : str, optional
        Base URL for the API endpoint.
    endpoint_action : str, optional
        Specific API action for the daily summary.
    request_template : dict, optional
        Base template for the request parameters.
    headers : dict, optional
        Additional headers to include in the request.
    fields : list of str, optional
        Fields to extract from the daily summary response, defaults to EXTRACTION_FIELDS.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the extracted daily summary data.

    Raises
    ------
    ValueError
        If required parameters (email, key, param, begin_date, end_date) are missing.
    """
    # Copy template to avoid modifying the original and update with provided parameters
    request_data = request_template.copy()
    if email_address:
        request_data['email'] = email_address
    if key:
        request_data['key'] = key
    if param:
        request_data['param'] = param
    if begin_date:
        request_data['begin_date'] = begin_date
    if end_date:
        request_data['end_date'] = end_date

    # Validate and set state and county FIPS if provided
    if fips and len(fips) == 5:
        request_data['state'] = fips[:2]
        request_data['county'] = fips[2:]

    # Ensure required fields are present
    required_fields = ['email', 'key', 'param', 'begin_date', 'end_date']
    for field in required_fields:
        if not request_data.get(field):
            raise ValueError(f"Must supply {field} to call 'request_daily_summary()'")

    # Construct the request URL
    request_url = endpoint_url + endpoint_action.format(**request_data)
    
    # Make the API request with throttling
    try:
        if API_THROTTLE_WAIT > 0.0:
            time.sleep(API_THROTTLE_WAIT)
        response = requests.get(request_url, headers=headers)
        response.raise_for_status()
        json_response = response.json()
        
        # Process and extract the summary data
        return extract_summary_from_response(json_response, fields=fields)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of request failure


def extract_summary_from_response(response: Optional[Dict[str, Any]] = None,
                                  fields: List[str] = EXTRACTION_FIELDS) -> pd.DataFrame:
    """
    Extracts a summary of specified fields from each record in the API response,
    organized by monitoring site, parameter, and date.

    Parameters
    ----------
    response : dict, optional
        API response containing data records, expected to have a "Data" key with a list of records.
    fields : list of str, optional
        List of field names to extract from each record. Default is EXTRACTION_FIELDS.

    Returns
    -------
    pd.DataFrame
        DataFrame summarizing extracted data by site, parameter, and date.
    """
    if response is None or "Data" not in response:
        print("No data found in the response.")
        return pd.DataFrame()  # Return an empty DataFrame if response data is missing

    # Initialize a list to accumulate extracted records
    records = []

    for record in response["Data"]:
        # Standardize date format to YYYYMMDD
        date = record.get('date_local', '').replace('-', '')
        
        # Structure record data with monitoring site and pollutant information
        record_data = {
            "site_id": record.get('site_number'),
            "local_site_name": record.get('local_site_name'),
            "site_address": record.get('site_address'),
            "state": record.get('state'),
            "county": record.get('county'),
            "city": record.get('city'),
            "date": date,
            "parameter_code": record.get('parameter_code'),
            "parameter_name": record.get('parameter'),
            "units_of_measure": record.get('units_of_measure'),
            "method": record.get('method')
        }

        # Extract specified fields, setting to None if a field is missing
        for field in fields:
            record_data[field] = record.get(field, None)
        
        # Add the structured record to the list
        records.append(record_data)

    # Convert list of records to a DataFrame
    return pd.DataFrame(records)    

def get_monitoring_stations_by_county(state_fips:int = AQS_REQUEST_TEMPLATE['state'],
                                      county_fips:int = AQS_REQUEST_TEMPLATE['county']):
    request_data = AQS_REQUEST_TEMPLATE.copy()
    if state_fips:
        request_data['state'] = state_fips
    if county_fips:
        request_data['county'] = county_fips
    response = request_list_info(request_template = request_data,
                                 endpoint_action  = API_ACTION_LIST_SITES)
    return response

def request_AQI_Pollutants():
    AQI_PARAM_CLASS = "AQI POLLUTANTS"
    request_data = AQS_REQUEST_TEMPLATE.copy()
    request_data['pclass'] = AQI_PARAM_CLASS
    response = request_list_info(request_template=request_data,
                                endpoint_action=API_ACTION_LIST_PARAMS)
    return response

def request_list_info(email_address: Optional[str] = None,
                      key: Optional[str] = None,
                      endpoint_url: str = API_REQUEST_URL,
                      endpoint_action: str = API_ACTION_LIST_CLASSES,
                      request_template: Dict[str, Any] = AQS_REQUEST_TEMPLATE,
                      headers: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """
    Request a list of information from the API, such as available classes or parameter
    descriptors, with required authentication and endpoint details.

    Parameters
    ----------
    email_address : str, optional
        The user's email address for API access, overrides email in the template if provided.
    key : str, optional
        The API key for authentication, overrides the key in the template if provided.
    endpoint_url : str
        The base URL for the API endpoint.
    endpoint_action : str
        The specific endpoint action to list information (e.g., classes or parameters).
    request_template : dict
        Template dictionary containing required API parameters.
    headers : dict, optional
        Optional headers to include in the request.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the data from the API response, or an empty DataFrame if the request fails.

    Raises
    ------
    Exception
        If the email or API key is not provided.
    """
    # Make a copy of the request template to avoid modifying the original
    request_data = request_template.copy()
    
    # Ensure email and key are set, prioritizing function parameters over template
    if email_address:
        request_data['email'] = email_address
    if key:
        request_data['key'] = key

    # Check for required fields
    if not request_data.get('email'):
        raise Exception("Must supply an email address to call 'request_list_info()'")
    if not request_data.get('key'):
        raise Exception("Must supply a key to call 'request_list_info()'")

    # Compose the request URL
    request_url = endpoint_url + endpoint_action.format(**request_data)
    
    # Make the API request with throttling to avoid rate limiting
    try:
        if API_THROTTLE_WAIT > 0.0:
            time.sleep(API_THROTTLE_WAIT)
        response = requests.get(request_url, headers=headers)
        response.raise_for_status()
        json_response = response.json()
        
        # Convert response data to DataFrame if available
        if "Data" in json_response:
            return pd.DataFrame(json_response["Data"])
        else:
            print("No data available in the response.")
            return pd.DataFrame()  # Return an empty DataFrame if no data is found
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if there's an error

