####################################################################################################
# This module contains functions that are to retrieve monthly page view
# data from the Wikimedia API and store it in a json file.

# This code is built from examples provided by wikimedia API documentation, 
# as well as code examples developed by Dr. David W. McDonald, for use in Data512,
# and covered under the Creative Commons CC-BY license.
####################################################################################################

#########
# IMPORTS
#########

# basic imports
import json
import time
import urllib.parse
from datetime import datetime, timedelta

# may require a pip install
import requests 

#################
#
# CONSTANTS
#
#################

# The Pageviews API asks that we not exceed 100 requests per second, 
# we add a small delay to each request
API_LATENCY_ASSUMED = 0.002       # 2ms
API_THROTTLE_WAIT = (1.0/100.0)-API_LATENCY_ASSUMED

# common URL/endpoint for all 'pageviews' API requests
API_REQUEST_PAGEVIEWS_ENDPOINT = 'https://wikimedia.org/api/rest_v1/metrics/pageviews/'
API_REQUEST_PER_ARTICLE_PARAMS = 'per-article/{project}/{access}/{agent}/{article}/{granularity}/{start}/{end}'

# Dates for the pageviews request
# format: YYYYMMDDHH
START_DATE = "2015010100"
END_DATE   =  get_previous_complete_month()




ACCESS_TYPES = ['desktop', 'mobile-app', 'mobile-web']


# The REST API 'pageviews' URL
# this is the common URL/endpoint for all 'pageviews' API requests
API_REQUEST_PAGEVIEWS_ENDPOINT = 'https://wikimedia.org/api/rest_v1/metrics/pageviews/'


# This template is used to map parameter values into the API_REQUST_PER_ARTICLE_PARAMS portion of an API request. The dictionary has a
# field/key for each of the required parameters. In the example, below, we only vary the article name, so the majority of the fields
# can stay constant for each request. Of course, these values *could* be changed if necessary.

ARTICLE_PAGEVIEWS_PARAMS_TEMPLATE = {
    "project":     "en.wikipedia.org",
    "access":      "desktop",      # this should be changed for the different access types
    "agent":       "user",
    "article":     "",             # this value will be set/changed before each request
    "granularity": "monthly",
    "start":       "2015010100",   # start and end dates need to be set
    "end":         "2023040100"    # this is likely the wrong end date
}

# This is a parameterized string that specifies what kind of pageviews request we are going to make
# In this case it will be a 'per-article' based request. The string is a format string so that we can
# replace each parameter with an appropriate value before making the request
API_REQUEST_PER_ARTICLE_PARAMS = 'per-article/{project}/{access}/{agent}/{article}/{granularity}/{start}/{end}'

def request_pageviews_for_article(article_title:str = None,
                                  request_header:dict = None, 
                                  endpoint_url:str = API_REQUEST_PAGEVIEWS_ENDPOINT, 
                                  endpoint_params:str = API_REQUEST_PER_ARTICLE_PARAMS, 
                                  request_template:dict = ARTICLE_PAGEVIEWS_PARAMS_TEMPLATE):
    """_summary_

    Parameters
    ----------
    article_title : str, optional
        _description_, by default None
    request_header : dict, optional
        _description_, by default REQUEST_HEADERS
    endpoint_url : str, optional
        The REST API 'pageviews' URL, by default API_REQUEST_PAGEVIEWS_ENDPOINT
    endpoint_params : str, optional
        a parameterized string that specifies the kind of pageviews request to make,
         requires the following format: 
        by default API_REQUEST_PER_ARTICLE_PARAMS
    request_template : dict, optional
        _description_, by default ARTICLE_PAGEVIEWS_PARAMS_TEMPLATE


    Returns
    -------
    _type_
        _description_

    Raises
    ------
    Exception
        _description_
    """

    # article title can be as a parameter to the call or in the request_template
    if article_title:
        request_template['article'] = article_title

    if not request_template['article']:
        raise Exception("Must supply an article title to make a pageviews request.")

    # Titles are supposed to have spaces replaced with "_" and be URL encoded
    article_title_encoded = urllib.parse.quote(request_template['article'].replace(' ','_'))
    request_template['article'] = article_title_encoded
    
    # now, create a request URL by combining the endpoint_url with the parameters for the request
    request_url = endpoint_url+endpoint_params.format(**request_template)
    
    # make the request
    try:
        # we'll wait first, to make sure we don't exceed the limit in the situation where an exception
        # occurs during the request processing - throttling is always a good practice with a free
        # data source like Wikipedia - or other community sources
        if API_THROTTLE_WAIT > 0.0:
            time.sleep(API_THROTTLE_WAIT)
        response = requests.get(request_url, headers=request_header)
        json_response = response.json()
    except Exception as e:
        print(e)
        json_response = None
    return json_response


def clean_article_title(article_title:str)->str:
    """_summary_

    Parameters
    ----------
    article_title : str
        _description_

    Returns
    -------
    _type_
        _description_
    """
    # Titles are supposed to have spaces replaced with "_" and be URL encoded
    article_title_encoded = urllib.parse.quote(request_template['article'].replace(' ','_'))
    request_template['article'] = article_title_encoded
    return article_title.replace(' ','_')



#################
#
# UTILITY FUNCTIONS
#
#################
def get_previous_complete_month()->str:
    """Gets the last day of the previous month in the 
    format YYYYMMDD00 

    Returns
    -------
    str
        string representation of the last day of the previous month
    """
    today = datetime.today()
    first_day_this_month = today.replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    ## Put in desired format
    date_str = last_day_last_month.strftime('%Y%m%d') + "00"
    return date_str