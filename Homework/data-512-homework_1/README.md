# Wikipedia Rare Diseases Pageview Analysis

## Project Goal

The goal of this project is to collect, analyze, and document monthly pageviews for a set of rare disease-related articles from English Wikipedia. Using the Wikimedia REST API, the project retrieves pageview data for each article from July 2015 through the most recent complete month (September 2024). The pageview data is collected separately for desktop and mobile access (including both mobile web and mobile app views). 

This project follows best practices for open scientific research and reproducibility, documenting all steps for data acquisition, processing, and analysis. The resulting dataset is stored in JSON format, and the analysis is presented in a Jupyter Notebook, providing visualizations of the trends over time.

## License of the Source Data

The source data used in this project is retrieved from the Wikimedia Foundation's Pageviews API. The data is licensed under the Wikimedia Foundation's [Terms of Use](https://foundation.wikimedia.org/wiki/Terms_of_Use/en). The project uses publicly available pageview data from Wikipedia, which adheres to the terms regarding proper use of open data, including the following:
- Attribution: Proper attribution of the source (Wikimedia Foundation).
- Usage: The data is used for analysis and research in accordance with the Wikimedia Foundation's guidelines.

Other data, including the csv of rare diseases and example code (located in the provided resources folder), was developed by Dr. David W. McDonald, for use in Data512, and covered under the Creative Commons CC-BY license. The code examples were used as a base for further development into functions found in the `access_wiki_pageviews.py` module

## API Documentation

The following API was used to gather data for this project:
- [Wikimedia Pageviews API Documentation](https://wikitech.wikimedia.org/wiki/Analytics/AQS/Pageviews)

This API provides access to pageview statistics for desktop, mobile-web, and mobile-app traffic on Wikipedia articles. The data is retrieved at monthly granularity.

## Data Files and Code

### Python Module
- `access_wiki_pageviews.py`: This script contains functions to retrieve monthly pageview data from the Wikimedia API, process it, and save it in JSON format.

### Jupyter Notebook
- `rare_diseases_pageviews_demo.ipynb`: This notebook demonstrates how to use the `access_wiki_pageviews.py` script to acquire pageview data from the Wikimedia API, as well as how to clean, process, and visualize the data.

### Input Files
- `rare-disease_cleaned_AUG2024.csv` : contains information on rare diseases, and has the columns 
   - disease
   - pageid
   - url

### Intermediary Files
- `rare-disease_monthly_desktop_<startYYYYMM>-<endYYYYMM>.json`: Contains monthly pageview counts for desktop access.
- `rare-disease_monthly_mobile_<startYYYYMM>-<endYYYYMM>.json`: Contains monthly pageview counts for mobile access (web + app combined).
- `rare-disease_monthly_cumulative_<startYYYYMM>-<endYYYYMM>.json`: Contains cumulative monthly pageview counts (desktop + mobile).


## Data Schema
All intermediate json files have the same type of data schema, which is as follows:
- `{project}` is `en.wikipedia.org` (English Wikipedia)
- `{article}` is the URL-encoded title of the Wikipedia article
- `{granularity}` is `monthly`
- `{timestamp}` is a string yyyymmddhh
- `{access}` can be `desktop`, `mobile-web`, or `mobile-app`
- `{agent}` is `user`
- `{views}` is an integer number of views of that article for that month

### Example Record in JSON:
```
{
  "Article_Title": [
    {
       {'project': 
        'article': 
        'granularity': 
        'timestamp': 
        'access': 
        'agent': 
        'views': }
    },
    ...
  ]
}
```

### Final Output Files
- Visualizations:
  - `top_10_peak_pageviews.png`: Time series plot showing the top 10 articles by peak pageviews for desktop and mobile access.
  - `fewest_months_of_data.png`: Time series plot showing the articles with the fewest months of available data for desktop and mobile access.
  - `max_min_average_pageviews.png`: Time series plot showing the articles with the highest and lowest average pageviews for desktop and mobile access.

### Known Issues and Special Considerations
- Data Gaps: Some articles may have missing months of data, which results in shorter time series for certain articles. This can happen if the article was created after the start date (July 1, 2015) or if there were technical issues with data collection during certain months.
- Mobile Data Aggregation: Mobile access data is aggregated from two sources: mobile-web and mobile-app. These are combined in this dataset for simplicity.
- Data Accuracy: Pageview data may include automated bot traffic that cannot always be excluded. Some anomalies in pageviews may be observed due to this.