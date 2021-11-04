import openpyxl
import requests
import bs4
import logging
import pandas as pd
import numpy as np
from typing import Dict, Tuple


def fix_ticker_formatting(filename: str,
                          save_filename: str,
                          column: str) -> None:
    workbook = openpyxl.load_workbook(filename=filename)
    ws = workbook.active # Opens the workbook.
    col = ws[column]

    for cell in col:
        ticker_data = cell.value.split('-')

        len_diff: int = 4 - len(ticker_data[0])
        ticker_data[0] = f'{"0"*len_diff}{ticker_data[0]}'
        # This line adds 0's in front of ticker number if needed, to
        # make sure that the length of the num is 4.
        
        # The tickers in our file contained dashes instead of dots. 
        # (example: 123-HK). However, on Yahoo finance, the urls use the
        # tickers with . instead of - and this line adds the . back in, as the
        # - has already been removed.
        cell.value = '.'.join(ticker_data) 
    workbook.save(filename=save_filename)


def get_headers() -> Dict[str, str]:
    return {"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7",
    "cache-control": "max-age=0",
    "dnt": "1",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"}


def get_debt_shares(bal_url: str, ticker: str) -> Tuple[float, float, float, float]:

    r = requests.get(bal_url, verify=True, headers=get_headers(), timeout=30)
    if r.status_code != 200: # 200 is successful request.
        logging.error(f'Status code error:{r.status_code}\n{bal_url}\n')
        return (-1.0, -1.0, -1.0, -1.0)
    soup = bs4.BeautifulSoup(r.text, 'lxml')
    
    # Gets a list of bs4 tags that have these elements in them, then uses list
    # indexing to obtain the one that we need and then gets the text for it. 
    # Removes commas, and the resulting number in str form is converted to a 
    # float.
    shares_20, shares_19, debt_20, debt_19 = -1.0, -1.0, -1.0, -1.0
    try:
        shares_20 = float(soup.select('div section span')[-3].text.replace(',','')) # 2020 shares
    except Exception as err:
        logging.error(f'Scraping error: shares20\n {err}\n url: {bal_url}\n ticker: {ticker}')
    
    try:
        shares_19 = float(soup.select('div section span')[-2].text.replace(',','')) # 2019 shares
    except Exception as err:
        logging.error(f'Scraping error: shares19\n {err}\n url: {bal_url}\n ticker: {ticker}')
    
    try:
        debt_20 = float(soup.select('div section span')[-15].text.replace(',','')) # 2020 total debt
    except Exception as err:
        logging.error(f'Scraping error: debt20\n {err}\n url: {bal_url}\n ticker: {ticker}')
    
    try:
        debt_19 = float(soup.select('div section span')[-14].text.replace(',','')) # 2019 total debt
    except Exception as err:
        logging.error(f'Scraping error: debt19\n {err}\n url: {bal_url}\n ticker: {ticker}')

    return (shares_20, shares_19, debt_20, debt_19)


def get_hist_price(price_url: str, ticker: str) -> Tuple[float, float]:
    
    r = requests.get(price_url, verify=True, headers=get_headers(), timeout=30)
    if r.status_code != 200: # 200 is successful request.
        logging.error(f'Status code error:{r.status_code}\n{price_url}\n')
        return (-1.0, -1.0)
    soup = bs4.BeautifulSoup(r.text, 'lxml')

    # Gets a list of bs4 tags that have element td in them, and then selects 
    # the one that that we need with list indexing, gets its text, and
    # converts it to a float.
    price20, price19 = -1.0, -1.0
    try:
        price20 = float(soup.find_all('td')[4].text)
    except Exception as err:
        logging.error(f'Scraping error: price20\n {err}\n url: {price_url}\n ticker: {ticker}')

    try:
        price19 = float(soup.find_all('td')[92].text)
    except Exception as err:
        logging.error(f'Scraping error: price19\n {err}\n url: {price_url}\n ticker: {ticker}')

    return (price20, price19)


def get_revenue_ebit(inc_url: str, ticker: str) -> Tuple[float, float, float, float]:

    r = requests.get(inc_url, verify=True, headers=get_headers(), timeout=30)
    if r.status_code != 200: # 200 is successful request.
        logging.error(f'Status code error:{r.status_code}\n{inc_url}\n')
        return (-1.0, -1.0, -1.0, -1.0)
    soup = bs4.BeautifulSoup(r.text, 'lxml')

    # Gets a list of bs4 tags that have these elements in them, then uses list
    # indexing to obtain the one that we need and then gets the text for it. 
    # Removes commas, and the resulting number in str form is converted to a 
    # float.
    rev20, rev19, ebit20, ebit19 = -1.0, -1.0, -1.0, -1.0
    try:
        rev20 = float(soup.select('div section span')[-160].text.replace(',',''))
    except Exception as err:
        logging.error(f'Scraping error: rev20\n {err}\n url: {inc_url}\n ticker: {ticker}')

    try:
        rev19 = float(soup.select('div section span')[-161].text.replace(',',''))
    except Exception as err:
        logging.error(f'Scraping error: rev19\n {err}\n url: {inc_url}\n ticker: {ticker}')

    try:
        ebit20 = float(soup.select('div section span')[-53].text.replace(',',''))
    except Exception as err:
        logging.error(f'Scraping error:  ebit20\n{err}\n url: {inc_url}\n ticker: {ticker}')

    try:
        ebit19 = float(soup.select('div section span')[-52].text.replace(',',''))
    except Exception as err:
        logging.error(f'Scraping error: ebit19\n{err}\n url: {inc_url}\n ticker: {ticker}')
    
    return (rev20, rev19, ebit20, ebit19)
    

def get_urls(ticker: str) -> Tuple[str, str, str]: 
    # Historical price is sourced from here.
    hist_price_url = f'https://finance.yahoo.com/quote/{ticker}/history?period1=1478131200&period2=1609372800&interval=1mo&filter=history&frequency=1mo&includeAdjustedClose=true'

    # debt and share number sourced from here.
    bal_sheet_url = f'https://finance.yahoo.com/quote/{ticker}/balance-sheet?p={ticker}'

    # All other metrics sourced from here.
    inc_stmt_url = f'https://finance.yahoo.com/quote/{ticker}/financials?p={ticker}'
    
    return (hist_price_url, bal_sheet_url, inc_stmt_url)


if __name__ == '__main__':
    pass