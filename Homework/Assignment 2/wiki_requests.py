import os
import time
import json
import requests
import urllib.parse
import pandas as pd
from typing import Any, Dict, List, Optional

#################
#
# CONSTANTS
#
#################
EMAIL = "rollk@uw.edu"
USER_AGENT_STR = "{EMAIL}, University of Washington, MSDS DATA 512 - AUTUMN 2024"
USERNAME = "DowntonCrabby"
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI0NTk0YTFjNGJlMmIyMjVlOGY5NjBiMDg3NDhjNGRmNSIsImp0aSI6IjVhMDY2M2E4OWE2MjU4YzViOTlhOGY0Zjc3YjMyMGU2NmZiNzlhOTU1ZTE2YTA5Mzk4MzM0ZDhiYjRjMzdhZWE3MjMzYzc3MjNkYTdkZjVhIiwiaWF0IjoxNzI4Nzg1NDI3LjczMjMwMywibmJmIjoxNzI4Nzg1NDI3LjczMjMwNywiZXhwIjozMzI4NTY5NDIyNy43MzAyNDQsInN1YiI6Ijc2NzAyOTE1IiwiaXNzIjoiaHR0cHM6Ly9tZXRhLndpa2ltZWRpYS5vcmciLCJyYXRlbGltaXQiOnsicmVxdWVzdHNfcGVyX3VuaXQiOjUwMDAsInVuaXQiOiJIT1VSIn0sInNjb3BlcyI6WyJiYXNpYyJdfQ.anuC2cjC67SIvr9H2Mjktp6TqxJbGFyjP1wxWvb7lv7PkP30c8VIyadng0iN8HXkQxpQb4A4j3N2JmiXXBxzNKBtf94WuAp9rCh0dgR-Gmj6CdqoWGrNglKJB_dFK4NboJi826shrrl7Zd2IRfpSzXzFsTCNvb6LiNp9n4-lYo_e3QPspyt6-YIYIU2D9J_Fnli2IdBPohH7Wm9Rj8AlcwgjURN_Msn44p56WI0QCCS5Z8FAEEZYhHMZT4-d_q8semz7dsr6Va_B9IvmJ8a-L7JVsMo1IxtZ1DW7V-XIkB-dEzDFNQk41nH680IhtHFqhOpBYab0217-qDlXVB2ySSpIjFLmAntx0uUk5urdXZY6Kmu521E6Shxb8LVRD9jCHvkXMy75EnAhIexYuw4aO6wB5Qr6Zwp4NHCfpg05dU9mYR5FUHeFEw2hxKX4JtXU6riZGRl60AZDcaYOK0yw2IOQ_X9QK1l32Cb7IiikQb1pWCg2tKvBsvleHYUi4l2GI8ehwsKG2Hn8S2JjsCUQzdJvUEOVqW15RBLxbZVrsipzgue8eHHF7C01iqaC9B8yYg0QtAVpbTrpM8u_UrC0E8tIyLRajSPy7Tzhhz4REYjpFKIS8HD3LYALZfjB-DbMy4w9O1xI6VZvM0mcoXGZ2X7BX3mIp0AIBW3OTpHlcEs"

#####  
# 1. API endpoints and models  
#####
# The LiftWing ORES API endpoint and prediction model
API_ORES_LIFTWING_ENDPOINT = "https://api.wikimedia.org/service/lw/inference/v1/models/{model_name}:predict"
API_ORES_EN_QUALITY_MODEL = "enwiki-articlequality"

# The basic English Wikipedia API endpoint
API_HEADER_AGENT = 'User-Agent'
API_ENWIKIPEDIA_ENDPOINT = "https://en.wikipedia.org/w/api.php"


#####
# 2. Throttling and rate limits
#####
# Assumed latency and throttling for LiftWing API
API_LATENCY_ASSUMED = 0.002       # Assuming roughly 2ms latency on the API and network
API_THROTTLE_WAIT = ((60.0 * 60.0) / 5000.0) - API_LATENCY_ASSUMED  # LiftWing key authorizes 5000 requests per hour

# Assumed throttling for Wikipedia API (100 requests/second)
API_THROTTLE_WAIT_ENWIKI = (1.0 / 100.0) - API_LATENCY_ASSUMED


#####
# 3. Request headers
#####
# LiftWing API request headers with authorization
REQUEST_HEADER_TEMPLATE = {
    'User-Agent': {USER_AGENT_STR},
    'Content-Type': 'application/json',
    'Authorization': "Bearer {ACCESS_TOKEN}"}

# Wikipedia API headers
REQUEST_HEADERS = {
    'User-Agent': {USER_AGENT_STR}
}

# Template for request parameters (to be filled with actual values)
REQUEST_HEADER_PARAMS_TEMPLATE = {
    'email_address': {EMAIL},   # Your email address should go here
    'access_token': {ACCESS_TOKEN}}


#####
# 4. Article revisions and page information
#####
# Template for ORES request payload (required data)
ORES_REQUEST_DATA_TEMPLATE = {
    "lang": "en",     # Required that it's English - we're scoring English Wikipedia revisions
    "rev_id": "",     # This request requires a revision id
    "features": True}

# Additional page properties to request from Wikipedia API (optional)
PAGEINFO_EXTENDED_PROPERTIES = "talkid|url|watched|watchers"

# Template for making requests to the Wikipedia API for page information
PAGEINFO_PARAMS_TEMPLATE = {
    "action": "query",
    "format": "json",
    "titles": "",           # Single page title at a time
    "prop": "info",
    "inprop": PAGEINFO_EXTENDED_PROPERTIES}


#####
# 5. ORES User authentication variables
#####



#################
#
# FUNCTIONS
#
#################

#####
# Utilities
#####

def prep_article_title(article_title: str) -> str:
    """
    Prepares the article title for use in a URL by replacing spaces with underscores
    and URL-encoding the title to ensure it is safe for use in API requests.

    Parameters
    ----------
    article_title : str
        The title of the Wikipedia article to be formatted.

    Returns
    -------
    str
        The formatted article title with spaces replaced by underscores and URL-encoded.
    """
    # Replace spaces in the article title with underscores,
    # as Wikipedia URLs use underscores instead of spaces
    prepped_title = article_title.replace(' ', '_')

    # URL-encode the article title to ensure it is safe for use in a URL
    # (e.g., handling special characters)
    encoded_title = urllib.parse.quote(prepped_title)

    return encoded_title


#####
# REQUESTS
#####


def request_pageinfo_per_article(
    article_title: Optional[str]     = None,
    endpoint_url: str                = API_ENWIKIPEDIA_ENDPOINT,
    request_template: Dict[str, Any] = PAGEINFO_PARAMS_TEMPLATE,
    headers: Dict[str, str]          = REQUEST_HEADERS
    ) -> Optional[Dict[str, Any]]:
    """
    Makes a request to the Wikipedia API to retrieve page information for a given article.

    Parameters:
    -----------
    article_title : Optional[str]
        The title of the Wikipedia article. This can be passed as a function parameter 
        or pre-populated in the request_template. If not provided, the request will fail.
    endpoint_url : str
        The Wikipedia API endpoint to send the request to (default is API_ENWIKIPEDIA_ENDPOINT).
    request_template : Dict[str, Any]
        The template for the parameters to be sent in the request.
    headers : Dict[str, str]
        The headers for the request, which must include the 'User-Agent' field containing a valid email address.
    
    Returns:
    --------
    Optional[Dict[str, Any]]
        The JSON response from the Wikipedia API as a dictionary, or None in case of an error.

    Raises:
    -------
    Exception:
        If the article title is missing, if 'User-Agent' is missing from headers, or if a placeholder email is used.
    """

    # Ensure the article title is included in the request
    if article_title:
        request_template['titles'] = article_title

    if not request_template['titles']:
        raise Exception("Must supply an article title to make a pageinfo request.")

    if API_HEADER_AGENT not in headers:
        raise Exception(f"The header data should include a '{API_HEADER_AGENT}' field that contains your UW email address.")

    if 'uwnetid@uw' in headers[API_HEADER_AGENT]:
        raise Exception(f"Use your UW email address in the '{API_HEADER_AGENT}' field.")

    # Make the request to the Wikipedia API
    try:
        # Throttle to avoid exceeding the API request limits
        if API_THROTTLE_WAIT > 0.0:
            time.sleep(API_THROTTLE_WAIT)
        response = requests.get(endpoint_url, headers=headers, params=request_template)
        json_response = response.json()
    except Exception as e:
        print(f"Error occurred: {e}")
        json_response = None

    return json_response

def request_ores_score_per_article(
    article_revid: Optional[int] = None,
    email_address: Optional[str] = None,
    access_token: Optional[str]  = None,
    endpoint_url: str = API_ORES_LIFTWING_ENDPOINT,
    model_name: str   = API_ORES_EN_QUALITY_MODEL,
    request_data: Dict[str, Any]  = ORES_REQUEST_DATA_TEMPLATE,
    header_format: Dict[str, str] = REQUEST_HEADER_TEMPLATE,
    header_params: Dict[str, str] = REQUEST_HEADER_PARAMS_TEMPLATE
    ) -> Optional[Dict[str, Any]]:
    """
    Makes a request to the ORES API to retrieve an article quality score for a given Wikipedia article revision.

    Parameters:
    -----------
    article_revid : Optional[int]
        The revision ID of the Wikipedia article to score. Required for the ORES request.
    email_address : Optional[str]
        The user's email address to include in the API request headers for identification. Required.
    access_token : Optional[str]
        The access token for authentication with the ORES API. Required.
    endpoint_url : str
        The LiftWing ORES API endpoint (default is API_ORES_LIFTWING_ENDPOINT).
    model_name : str
        The name of the ORES model to use (default is API_ORES_EN_QUALITY_MODEL).
    request_data : Dict[str, Any]
        The data payload to be sent in the request, including revision ID and features flag.
    header_format : Dict[str, str]
        The template for constructing request headers, with placeholders for email and access token.
    header_params : Dict[str, str]
        The dictionary containing values (email_address and access_token) to fill into the header template.

    Returns:
    --------
    Optional[Dict[str, Any]]
        The JSON response from the ORES API as a dictionary, or None in case of an error.

    Raises:
    -------
    Exception:
        If the revision ID, email address, or access token is missing.
    """

    # Ensure all required fields are provided
    if article_revid:
        request_data['rev_id'] = article_revid
    if email_address:
        header_params['email_address'] = email_address
    if access_token:
        header_params['access_token'] = access_token
    
    if not request_data['rev_id']:
        raise Exception("Must provide an article revision ID (rev_id) to score articles.")
    if not header_params['email_address']:
        raise Exception("Must provide an 'email_address' value.")
    if not header_params['access_token']:
        raise Exception("Must provide an 'access_token' value.")
    
    # Format the request URL and headers
    request_url = endpoint_url.format(model_name=model_name)
    
    headers = {key: header_format[key].format(**header_params) for key in header_format}
    
    # Make the request to the ORES API
    try:
        # Throttle to avoid exceeding the API request limits
        if API_THROTTLE_WAIT > 0.0:
            time.sleep(API_THROTTLE_WAIT)
        response = requests.post(request_url, headers=headers, data=json.dumps(request_data))
        json_response = response.json()
    except Exception as e:
        print(f"Error occurred: {e}")
        json_response = None

    return json_response



# Function to get the latest revision IDs for a batch of Wikipedia article titles
def fetch_revision_ids_for_batch(article_titles):
    """
    Fetches the latest revision IDs for a batch of Wikipedia articles using the Wikipedia API.

    Args:
        article_titles (list): A list of article titles to query.

    Returns
        dict: A dictionary mapping article titles to their respective revision IDs. 
        If an article is missing or a revision ID is not available, None is returned for that title.
    """
    try:
        # Join the titles with "|" to form a single request
        titles_query_str = "|".join(article_titles)

        # Define the parameters for the Wikipedia API query
        query_params = {
            "action": "query",
            "format": "json",
            "titles": titles_query_str,
            "prop": "info"
        }

        # Send the request to the Wikipedia API
        response = requests.get(API_ENWIKIPEDIA_ENDPOINT, headers=REQUEST_HEADERS, params=query_params)
        response_data = response.json()

        # Initialize dictionary to hold revision IDs
        article_revision_ids = {}

        # Process the response to extract revision IDs
        for page_id, page_data in response_data['query']['pages'].items():
            title = page_data.get('title', 'Unknown')
            if 'missing' in page_data:
                print(f"Article missing for title: {title}")
                article_revision_ids[title] = None  # Mark missing pages
            else:
                # Store the revision ID if available
                revision_id = page_data.get('lastrevid', None)
                if revision_id is None:
                    print(f"Revision ID missing for title: {title}")
                article_revision_ids[title] = revision_id

        return article_revision_ids

    except Exception as e:
        print(f"Error occurred while retrieving batch revision IDs: {e}")
        return {title: None for title in article_titles}  # Return None for all titles in case of failure


# Function to process all article titles in batches and retrieve their revision IDs
def fetch_revision_ids_for_all_articles(article_titles, batch_size=50):
    """
    Retrieves the revision IDs for a list of Wikipedia articles in batches to optimize API requests.

    Args:
        article_titles (list): A list of article titles for which to fetch revision IDs.
        batch_size (int, optional): The number of articles to query in each batch (default is 50).

    Returns:
        dict: A dictionary mapping article titles to their respective revision IDs.
    """
    
    all_revision_ids = {}

    # Loop over the article titles in batches
    for batch_start in range(0, len(article_titles), batch_size):
        batch_titles = article_titles[batch_start:batch_start + batch_size]
        batch_revision_ids = fetch_revision_ids_for_batch(batch_titles)
        all_revision_ids.update(batch_revision_ids)

        # Delay to avoid overwhelming the API with requests
        time.sleep(0.1)

    return all_revision_ids