[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

# Yahoo Finance Scraper for Hang Seng Index

Created this webscraper to gather data for my group project for Energy and Environmental Economics, a course at my university (junior year).

My group selected ESG Investing as our broad scope topic, and focused on carbon intensity metrics - methods of quantifying the carbon footprint of a company relative to its growth and earnings. We hypothesised that with the rise in popularity of ESG investing, a company with a consistently smaller carbon footprint after normalisation, would see better stock returns in the long term. We specifically examined two popular metrics, WACI and Relative Carbon Intensity, and compared how closely they correlated with the revenue of and stock returns for different companies. 

### Data Scraping

My main task here was to get data for all 60 components of the Hang Seng Index, which ended up being 840 total data points, and would require visiting 180 different webpages. I decided to write a Python webscraper using the Requests, BeautifulSoup and lxml libraries, which would retrieve the data from Yahoo Finance. This would also be scalable in case we decided to expand our dataset for the study.

I designed the scraper so that it takes in an Excel file with a column containing the tickers for the index. It then formats these to make them usable in Yahoo Finance URLs and saves the resulting tickers in a new Excel file (leaving your original file as is, for data integrity).

It then opens this newly created file, creates URLs for each ticker, and then scrapes the data from each page. The data is temporarily stored in a pandas dataframe, and once scraping is complete writes it to an output Excel file, whose name can be set.
It logs any errors in the scraper.log file.

The webscraper carries out this task in 15-20 minutes. The scraping actually takes less time, but I've added random delays to prevent the scraper from making too many requests in a short timeframe (might get blocked then).

#### Target data

* stock price
* total revenue
* total debt
* EBIT
* total issued shares number

*Stock price data is scraped for 2017, 2018, 2019, 2020. The rest of the data is scraped only for 2019, 2020.*

### To run

1. Clone into repo/download zip file
2. Make an excel file with your own list of tickers (doesn't have to be hang seng index)

https://user-images.githubusercontent.com/68847270/143286827-f5dee46f-bfdf-4abf-b062-3e7eff074aaf.mp4



https://user-images.githubusercontent.com/68847270/143286994-325e6afa-716b-4f06-a9df-943caf7ef359.mp4


OR

Use the existing file

3. Ensure that you have bs4, requests, lxml, numpy, pandas, openpyxl all installed.
4. Run main.py (Should give you updates on scraping progress in terminal).

