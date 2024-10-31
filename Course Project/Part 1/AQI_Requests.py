

##################
#
#    IMPORTS
###################


import json
import time
import requests
import pandas as pd
from typing import Any, Dict, List, Optional, Tuple, Union  

##################
#
#   API CONSTANTS
###################

#
#    This is the root of all AQS API URLs
#
API_REQUEST_URL = 'https://aqs.epa.gov/data/api'

#
#    These are some of the 'actions' we can ask the API to take or requests that we can make of the API
#
#    List actions provide information on API parameter values that are required by some other actions/requests
API_ACTION_LIST_CLASSES = '/list/classes?email={email}&key={key}'
API_ACTION_LIST_PARAMS = '/list/parametersByClass?email={email}&key={key}&pc={pclass}'
API_ACTION_LIST_SITES = '/list/sitesByCounty?email={email}&key={key}&state={state}&county={county}'
#
#    Monitor actions are requests for monitoring stations that meet specific criteria
API_ACTION_MONITORS_COUNTY = '/monitors/byCounty?email={email}&key={key}&param={param}&bdate={begin_date}&edate={end_date}&state={state}&county={county}'
API_ACTION_MONITORS_BOX = '/monitors/byBox?email={email}&key={key}&param={param}&bdate={begin_date}&edate={end_date}&minlat={minlat}&maxlat={maxlat}&minlon={minlon}&maxlon={maxlon}'
#
#    Summary actions are requests for summary data. These are for daily summaries
API_ACTION_DAILY_SUMMARY_COUNTY = '/dailyData/byCounty?email={email}&key={key}&param={param}&bdate={begin_date}&edate={end_date}&state={state}&county={county}'
API_ACTION_DAILY_SUMMARY_BOX = '/dailyData/byBox?email={email}&key={key}&param={param}&bdate={begin_date}&edate={end_date}&minlat={minlat}&maxlat={maxlat}&minlon={minlon}&maxlon={maxlon}'
#
#    It is always nice to be respectful of a free data resource.
#    We're going to observe a 100 requests per minute limit - which is fairly nice
API_LATENCY_ASSUMED = 0.002       # Assuming roughly 2ms latency on the API and network
API_THROTTLE_WAIT = (1.0/100.0)-API_LATENCY_ASSUMED
#
#
#    This is a template that covers most of the parameters for the actions we might take, from the set of actions
#    above. In the examples below, most of the time parameters can either be supplied as individual values to a
#    function - or they can be set in a copy of the template and passed in with the template.
# 
AQS_REQUEST_TEMPLATE = {
    "email":      "kateroll@gmail.com",     
    "key":        "silverfox66",      
    "state":      "12",     # the two digit state FIPS # as a string
    "county":     "073",     # the three digit county FIPS # as a string
    "begin_date": "",     # the start of a time window in YYYYMMDD format
    "end_date":   "",     # the end of a time window in YYYYMMDD format, begin_date and end_date must be in the same year
    "minlat":    0.0,
    "maxlat":    0.0,
    "minlon":    0.0,
    "maxlon":    0.0,
    "param":     "",     # a list of comma separated 5 digit codes, max 5 codes requested
    "pclass":    ""      # parameter class is only used by the List calls
}

USERNAME = "kateroll@gmail.com"
EMAIL = "kateroll@gmail.com"
APIKEY = "silverfox66"


##################
def fetch_monitoring_stations(bounding_box: Dict[str, float],
                              api_key: str = APIKEY,
                              email: str = EMAIL,
                              headers: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """
    Retrieve monitoring stations within the bounding box.

    Parameters
    ----------
    bounding_box : dict
        Bounding box with min and max latitude and longitude.
    api_key : str, optional
        API key for accessing the service. Default is APIKEY.
    email : str, optional
        Email for API authentication. Default is EMAIL.
    headers : dict, optional
        Optional headers for API request.

    Returns
    -------
    pd.DataFrame
        DataFrame containing details of the monitoring stations within the bounding box.
    """
    # Construct the API request
    request_params = {
        'api_key': api_key,
        'email': email,
        'min_lat': bounding_box['min_lat'],
        'max_lat': bounding_box['max_lat'],
        'min_lon': bounding_box['min_lon'],
        'max_lon': bounding_box['max_lon']
    }
    response = requests.get("API_ENDPOINT_MONITORING_STATIONS", params=request_params, headers=headers)

    # Check for errors
    response.raise_for_status()
    stations_data = response.json().get("Data", [])

    # Convert to DataFrame
    return pd.DataFrame(stations_data)



def request_monitors(email_address: Optional[str] = USERNAME, 
                     key: Optional[str] = APIKEY,
                     param: Optional[str] = None, 
                     begin_date: Optional[str] = None,end_date: Optional[str] = None, 
                     fips: Optional[str] = None,
                     endpoint_url: str = API_REQUEST_URL, 
                     endpoint_action: str = API_ACTION_MONITORS_COUNTY,
                     request_template: Dict[str, Any] = AQS_REQUEST_TEMPLATE,
                     headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
    """
    Requests monitoring stations information from the API, with options for 
    filtering by state, county, or bounding box.

    Parameters
    ----------
    email_address : str, optional
        User email address for API access. Default is None.
    key : str, optional
        API key for authentication. Default is None.
    param : str, optional
        Parameter code to request specific measurements. Default is None.
    begin_date : str, optional
        Start date for data retrieval (YYYYMMDD format). Default is None.
    end_date : str, optional
        End date for data retrieval (YYYYMMDD format). Default is None.
    fips : str, optional
        FIPS code for the state and county. Default is None.
    endpoint_url : str, optional
        Base URL for the API endpoint. Default is API_REQUEST_URL.
    endpoint_action : str, optional
        Action to specify in API call. Default is API_ACTION_MONITORS_COUNTY.
    request_template : dict, optional
        Template for API request parameters. Default is AQS_REQUEST_TEMPLATE.
    headers : dict, optional
        Headers for the API request. Default is None.

    Returns
    -------
    dict or None
        JSON response from the API if successful, otherwise None.
    """
    # Overwrite template with provided parameters, if any
    if email_address:
        request_template['email'] = email_address
    if key:
        request_template['key'] = key
    if param:
        request_template['param'] = param
    if begin_date:
        request_template['begin_date'] = begin_date
    if end_date:
        request_template['end_date'] = end_date
    if fips and len(fips) == 5:
        request_template['state'] = fips[:2]
        request_template['county'] = fips[2:]

    # Ensure required parameters are present
    if not all(request_template[key] for key in ['email', 'key', 'param', 'begin_date', 'end_date']):
        raise Exception("Must supply email, key, param, begin_date, and end_date for 'request_monitors'")

    # Prepare request URL
    request_url = endpoint_url + endpoint_action.format(**request_template)

    # Send request and parse response
    try:
        if API_THROTTLE_WAIT > 0.0:
            time.sleep(API_THROTTLE_WAIT)  # Throttling request for API rate limits
        response = requests.get(request_url, headers=headers)
        return response.json()
    except Exception as e:
        print(e)
        return None

#
#   Given the set of sensor codes, now we can create a parameter list or 'param' value as defined by the AQS API spec.
#   It turns out that we want all of these measures for AQI, but we need to have two different param constants to get
#   all seven of the code types. We can only have a max of 5 sensors/values request per param.
#
#   Gaseous AQI pollutants CO, SO2, NO2, and O2
AQI_PARAMS_GASEOUS = "42101,42401,42602,44201"
#
#   Particulate AQI pollutants PM10, PM2.5, and Acceptable PM2.5
AQI_PARAMS_PARTICULATES = "81102,88101,88502"
#   
#
AQI_PARAM_CLASS = "AQI POLLUTANTS"

#
#    This is a list of field names - data - that will be extracted from each record
#
EXTRACTION_FIELDS = ['sample_duration','observation_count','arithmetic_mean','aqi']

def fetch_aqi_readings(station_id: str,
                       start_date: str,
                       end_date: str,
                       params: List[str],
                       api_key: str = APIKEY,
                       email: str = EMAIL,
                       headers: Optional[Dict[str, str]] = None) -> pd.DataFrame:
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
    api_key : str, optional
        API key for accessing the service. Default is APIKEY.
    email : str, optional
        Email for API authentication. Default is EMAIL.
    headers : dict, optional
        Optional headers for API request.

    Returns
    -------
    pd.DataFrame
        DataFrame containing AQI readings for the specified station, date range, and parameters.
    """
    request_params = {
        'api_key': api_key,
        'email': email,
        'station_id': station_id,
        'start_date': start_date,
        'end_date': end_date,
        'parameters': ','.join(params)
    }
    response = requests.get("API_ENDPOINT_AQI_READINGS", params=request_params, headers=headers)

    # Check for errors
    response.raise_for_status()
    aqi_data = response.json().get("Data", [])

    # Convert to DataFrame
    return pd.DataFrame(aqi_data)

def extract_summary_from_response(response: Optional[Dict[str, Any]] = None,
                                  fields: List[str] = EXTRACTION_FIELDS) -> pd.DataFrame:
    """
    Extracts a summary of specified fields from each record in the response,
    organized by monitoring site, parameter, and date, and returns it as a
    pandas DataFrame.

    Parameters
    ----------
    response : dict, optional
        API response containing data records. Default is None.
    fields : list of str, optional
        List of field names to extract from each record. Default is EXTRACTION_FIELDS.

    Returns
    -------
    pd.DataFrame
        DataFrame summarizing extracted data by site, parameter, and date.
    """
    # Check if response data is available
    if not response or "Data" not in response:
        return pd.DataFrame()  # Return an empty DataFrame if response data is missing

    # Initialize list to store data for DataFrame conversion
    records = []

    # Iterate over each record in the response data
    for record in response["Data"]:
        # Prepare record details
        site_id = record['site_number']
        parameter_code = record['parameter_code']
        date_key = record['date_local'].replace('-', '')  # Format date as YYYYMMDD

        # Extract relevant fields into a dictionary
        extracted_data = {
            "site_id": site_id,
            "local_site_name": record['local_site_name'],
            "site_address": record['site_address'],
            "state": record['state'],
            "county": record['county'],
            "city": record['city'],
            "parameter_code": parameter_code,
            "parameter_name": record['parameter'],
            "units_of_measure": record['units_of_measure'],
            "method": record['method'],
            "date": date_key,
        }

        # Add each requested field to the dictionary
        for field in fields:
            extracted_data[field] = record.get(field, None)

        # Append the structured data to records list
        records.append(extracted_data)

    # Convert list of records to a pandas DataFrame
    return pd.DataFrame(records)


##################
#
#   UTILITIES
###################

LAT_25MILES = 25.0 * (1.0 / 69.0)  # Approx. 25 miles of latitude in decimal degrees
LON_25MILES = 25.0 * (1.0 / 54.6)  # Approx. 25 miles of longitude in decimal degrees

def bounding_latlon(place: Optional[Dict[str, List[float]]] = None, 
                    scale: float = 1.0) -> List[float]:
    """
    Calculates a bounding box around a given location, extending the latitude
    and longitude by an approximate distance in miles.

    Parameters
    ----------
    place : dict, optional
        A dictionary containing latitude and longitude coordinates as 
        'latlon' key. Default is None.
    scale : float, optional
        A scaling factor to extend the distance of the bounding box. 
        Default is 1.0.

    Returns
    -------
    list of float
        A list with minimum and maximum latitude and longitude for the 
        bounding box: [min_lat, max_lat, min_lon, max_lon].
    """
    min_lat = place['latlon'][0] - scale * LAT_25MILES
    max_lat = place['latlon'][0] + scale * LAT_25MILES
    min_lon = place['latlon'][1] - scale * LON_25MILES
    max_lon = place['latlon'][1] + scale * LON_25MILES
    return [min_lat, max_lat, min_lon, max_lon]