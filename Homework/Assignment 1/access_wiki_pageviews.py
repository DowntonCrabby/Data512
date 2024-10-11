####################################################################################################
# This module contains functions that are to retrieve monthly page view
# data from the Wikimedia API and store it in a json file.

# This code is built from examples provided by wikimedia API documentation, 
# as well as code examples developed by Dr. David W. McDonald, for use in Data512,
# and covered under the Creative Commons CC-BY license.
####################################################################################################


#################
#
# IMPORTS
#
#################

import os
import json
import time
import pandas as pd
import urllib.parse
from datetime import datetime, timedelta

# may require a pip install
import requests 


#################
#
# DATA ACQUISITION FUNCTIONS
#
#################

def set_request_header(user_email:str, 
                       organization:str,
                       project:str)->dict:
    """wiki API requires a specific header format for requests. 
    This function creates the header in the required format.

    Parameters
    ----------
    user_email : str
        email address of the user making the request
    organization : str
        organization making the request
    project : str
        description of the project making the request
    Returns
    -------
    dict
        a dict with the header information in the format required by the API:
        {'User-Agent': 'youremail@example.com, Your Organization, Your Project',}
    """
    request_header = {'User-Agent': '{}, {}, {}'.format(user_email, organization, project)}
    return request_header


def request_article_pageviews(article_title: str, 
                              start_date: str, 
                              end_date: str, 
                              access_type: str, 
                              request_header: dict,
                              latency_assumed: float = 0.002,  # Default latency of 2ms
                              throttle_wait: float = None) -> dict:
    """
    Makes an API request to retrieve pageviews for a specific
    article and access type.

    Parameters
    ----------
    article_title : str
        The title of the article to request pageviews for.
    start_date : str
        The start date for the pageview data in the format YYYYMMDDHH.
    end_date : str
        The end date for the pageview data in the format YYYYMMDDHH.
    access_type : str
        The type of access ('desktop', 'mobile-web', or 'mobile-app').
    headers : dict
        Request headers containing user information.
    latency_assumed : float, optional
        The assumed latency of API requests in seconds. Default is 2ms.
    throttle_wait : float, optional
        The time to wait between API requests to ensure the rate limit is respected.
        If not provided, it will be calculated as (1/100.0) minus latency_assumed.

    Returns
    -------
    dict
        A dictionary containing the pageview data.
    """
    # Prepare API endpoint and request parameters
    API_REQUEST_PAGEVIEWS_ENDPOINT = 'https://wikimedia.org/api/rest_v1/metrics/pageviews/'
    
    # This is a parameterized string that specifies what kind of pageviews 
    # request we are going to make In this case, it will be a 'per-article' based request.
    # The string is a format string so that we can replace each parameter
    # with an appropriate value before making the request.
    API_REQUEST_PER_ARTICLE_PARAMS = 'per-article/{project}/{access}/{agent}/{article}/{granularity}/{start}/{end}'

    # Calculate throttle wait time if not provided
    if throttle_wait is None:
        throttle_wait = (1.0 / 100.0) - latency_assumed

    article_title_encoded = prep_article_title(article_title)

    # Prepare the request URL
    request_url = API_REQUEST_PAGEVIEWS_ENDPOINT + API_REQUEST_PER_ARTICLE_PARAMS.format(
        project="en.wikipedia.org",
        access=access_type,
        agent="user",
        article=article_title_encoded,
        granularity="monthly",
        start=start_date,
        end=end_date
    )

    try:
        # Respect the throttle limit to avoid exceeding API rate limits
        time.sleep(throttle_wait)
        response = requests.get(request_url, headers=request_header)
        response.raise_for_status()  # Check for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving pageviews for {article_title} ({access_type}): {e}")
        return None


def save_json(data: dict, filename: str) -> None:
    """
    Saves data as a JSON file, ensuring that the directory exists.

    Parameters
    ----------
    data : dict
        The data to save in JSON format.
    filename : str
        The path (including the filename) wherethe JSON file will be saved.
    """
    # Ensure the directory exists
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Save the JSON file
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {filename}")


def combine_pageviews(mobile_web_views: dict,
                      mobile_app_views: dict) -> list:
    """
    Combines pageviews from mobile-web and
    mobile-app into one dataset.

    Parameters
    ----------
    mobile_web_views : dict
        The mobile-web pageviews data.
    
    mobile_app_views : dict
        The mobile-app pageviews data.

    Returns
    -------
    list
        A list of dictionaries with combined
        mobile-web and mobile-app views.
    """
    combined_views = []
    for web, app in zip(mobile_web_views['items'], mobile_app_views['items']):
        combined_views.append({
            'timestamp': web['timestamp'],
            'views': web['views'] + app['views']
        })
    return combined_views


def generate_pageview_datasets(articles_list: list,
                               start_date: str,
                               end_date: str,
                               request_header: dict) -> None:
    """
    Generates and saves jsons for  desktop, mobile, 
    and cumulative pageview data for the given list of
    articles.
    
    Parameters
    ----------
    articles : list of strings
        A list of article titles.
    start_date : str
        The start date in YYYYMMDD00 format.
    end_date : str
        The end date in YYYYMMDD00 format.
    request_header : dict
        The request header required by the Wikimedia API.
    
    return
    -------
    tuple of dicts
        desktop_data, mobile_data, cumulative_data
    """
    
    # Dictionaries to store pageviews for each article
    desktop_data = {}
    mobile_data = {}
    cumulative_data = {}

    count = 1
    num_articles = len(articles_list)
    for article in articles_list:
        print(f"Processing article: {article}, {count} of {num_articles}")

        # Fetch desktop pageviews
        desktop_views = request_article_pageviews(article,
                                                  start_date, end_date,
                                                  "desktop",
                                                  request_header)
        
        
        # If desktop_views is valid (i.e., not None), store
        # the 'items' (list of pageview records)

        # If desktop_views is None or invalid, store an empty list for that article
        desktop_data[article] = desktop_views['items'] if desktop_views else []

        # Fetch mobile-web and mobile-app views
        mobile_web_views = request_article_pageviews(article,
                                                     start_date, end_date,
                                                     "mobile-web",
                                                     request_header)
        
        mobile_app_views = request_article_pageviews(article,
                                                     start_date, end_date,
                                                     "mobile-app",
                                                     request_header)

        # Combine mobile-web and mobile-app views
        if mobile_web_views and mobile_app_views:
            mobile_data[article] = combine_pageviews(mobile_web_views,
                                                     mobile_app_views)
        else:
            mobile_data[article] = []

        # Cumulative data (desktop + mobile)
        # This combines the desktop and mobile pageviews for each month.
        # 'zip' pairs up corresponding months from both desktop and mobile lists.
        # It creates a new list of dictionaries with the 'timestamp' (from desktop)
        # and the combined 'views' (desktop views + mobile views for the same month).
        cumulative_data[article] = [
            {
                'timestamp': desktop['timestamp'],
                'views': desktop['views'] + mobile['views']
            }
            for desktop, mobile in zip(desktop_data[article], mobile_data[article])
        ]
        count += 1

    ### SAVE DAT DATA!
    ## formatted filenames
    # Named constant for slicing the year and month from date strings (YYYYMM)
    DATE_SLICE = 6
    start_date_str = start_date[:DATE_SLICE]
    end_date_str = end_date[:DATE_SLICE]

    save_json(desktop_data, f'rare-disease_monthly_desktop_{start_date_str}-{end_date_str}.json')
    save_json(mobile_data, f'rare-disease_monthly_mobile_{start_date_str}-{end_date_str}.json')
    save_json(cumulative_data, f'rare-disease_monthly_cumulative_{start_date_str}-{end_date_str}.json')

    return desktop_data, mobile_data, cumulative_data

#################
#
# UTILITY FUNCTIONS
#
#################

def prep_article_title(article_title:str)->str:
    """prepares the article title for use in a 
    URL by replacing spaces with underscores
    and URL encoding the title

    Parameters
    ----------
    article_title : str
        _description_

    Returns
    -------
    str
        _description_
    """
    # Replace spaces in the article title with underscores,
    # as Wikipedia URLs use underscores instead of spaces
    preped_title = article_title.replace(' ', '_')

    # URL-encode the article title to ensure it is safe for use in a URL
    # (e.g., handling special characters)
    encoded_title = urllib.parse.quote(preped_title)

    return encoded_title

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


def save_json(data: dict, filename: str) -> None:
    """
    Saves data as a JSON file and ensures that the directory exists.

    Parameters
    ----------
    data : dict
        The data to save in JSON format.
    filename : str
        The path (including the filename) where the JSON file will be saved.

    Returns
    -------
    None
    """
    # Get the directory from the filename
    directory = os.path.dirname(filename)
    
    # If the directory does not exist, create it
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Save the JSON file
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {filename}")