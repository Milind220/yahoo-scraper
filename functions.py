"""Functions to be used in scraper for Hang Seng Index data from Yahoo Finance.

The functions in this script are designed to be directly imported into the
main script of this program, but can be used externally as well, with
perhaps only minor tweaking.
"""


import logging
import random
import sys
import time
from typing import Dict, Tuple

import bs4
import lxml
import numpy as np
import openpyxl
import pandas as pd
import requests
from lxml import html

# TODO: address error highlights in get_hist_price.
# TODO: Add automatic currency conversion features.


def configure_logs(logfile_name: str = "scraper.log") -> None:
    """Configures settings for the script log.

    Args:
        logfile_name (str, optional): Name of the log file. Defaults to
            'scraper.log'.  
    """
    logging.basicConfig(
        filename=logfile_name,
        filemode="w",
        level=logging.ERROR,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    print(
        "\n\nStatus: Logs configured."
        f"\n\tLogs for this run can be found in {logfile_name}"
        "\n\tAll errors encountered are logged here."
    )


def fix_ticker_formatting(
    filename: str, save_filename: str, column: str = "A",
) -> None:
    """Fixes the formatting of the tickers to use in Yahoo Finance URLs.

    Reads in an Excel file with the tickers in it, and saves formatted tickers
    in a new Excel file.

    Args:
        filename (str): Name of Excel file with one column containing tickers.
        save_filename (str): Name that output file should be given. 
        column (str): index label for column that contains tickers. Defaults
            to 'A'.
    """
    workbook = openpyxl.load_workbook(filename=filename)
    ws = workbook.active
    col = ws[column]

    for cell in col:
        if cell.value == "\\":
            cell.value = "Ticker"
        ticker_data = cell.value.split("-")

        len_diff: int = 4 - len(ticker_data[0])
        ticker_data[0] = f'{"0"*len_diff}{ticker_data[0]}'
        # This line adds 0's in front of ticker number if needed, to
        # make sure that the length of the num is 4.

        # The tickers in our file contained dashes instead of dots.
        # (example: 123-HK). However, on Yahoo finance, the urls use
        # the tickers with . instead of - and this line adds the .
        # back in, as the - has already been removed.
        cell.value = ".".join(ticker_data)
    workbook.save(filename=save_filename)
    print("Status: Ticker formatting fixed.\n")


def generate_rand_delay(upper: int = 10, lower: int = 4) -> None:
    """Makes the scraper sleep for a random period of time.

    Sleep time is randomly selected from a uniform distribution between 'lower'
    and 'upper', including both end points.

    Args:
        upper (int, optional): Upper limit for sleep time. Defaults to 10.
        lower (int, optional): Lower limit for sleep time. Defaults to 4.
    """
    time.sleep(random.randint(lower, upper))


def get_debt_shares(
    bal_url: str, ticker: str,
) -> Tuple[
    float, float, float, float,
]:
    """Retrieves data on the total debt and no. of issued shares of company.

    This data is retrieved for the years 2020 and 2019.

    Args:
        bal_url (str): URL for the Yahoo finance webpage of the balance sheet
            of the company.
        ticker (str): Official ticker of the company, as used on Yahoo finance.

    Returns:
        Tuple[float, float, float, float]: Total shares in 2020, total shares
            in 2019, total debt in 2020, total debt in 2019.
    """
    r = requests.get(bal_url, verify=True, headers=_get_headers(), timeout=30)

    # For an unsuccessful request.
    if r.status_code != 200:
        logging.error(f"Status code error:{r.status_code}\n {bal_url}\n")
        return (-1.0, -1.0, -1.0, -1.0)

    soup = bs4.BeautifulSoup(r.text, "lxml")

    shares20, shares19, debt20, debt19 = -1.0, -1.0, -1.0, -1.0
    # In the event of an error if a value is not assigned, a -1.0 value
    # is assigned.

    # 2020 shares.
    try:

        shares20 = float(soup.select("div section span")[-4].text.replace(",", ""))
    except Exception:
        _log_error(bal_url, ticker, place="shares20")

    # 2019 shares.
    try:
        shares19 = float(soup.select("div section span")[-3].text.replace(",", ""))
    except Exception:
        _log_error(bal_url, ticker, place="shares19")

    # 2020 debt.
    try:
        for i, tag in enumerate(soup.select("div section span")):
            if tag.text == "Total Debt":
                debt20 = float(
                    soup.select("div section span")[i + 1].text.replace(",", "")
                )
    except Exception:
        _log_error(bal_url, ticker, place="debt20")

    # 2019 debt.
    try:
        for i, tag in enumerate(soup.select("div section span")):
            if tag.text == "Total Debt":
                debt19 = float(
                    soup.select("div section span")[i + 2].text.replace(",", "")
                )
    except Exception:
        _log_error(bal_url, ticker, place="debt19")

    return (shares20, shares19, debt20, debt19)


def get_revenue_ebit(inc_url: str, ticker: str) -> Tuple[float, float, float, float]:
    """Retrieves data on total revenue and EBIT of company.

    This data is retrieved for the years 2020 and 2019.
    
    Args:
        inc_url (str): URL for the Yahoo finance webpage of the income
            statement of the company.
        ticker (str): Official ticker of the company, as used on Yahoo finance.

    Returns:
        Tuple[float, float, float, float]: Revenue in 2020, revenue in 2019,
            EBIT in 2020, EBIT in 2019.
    """
    r = requests.get(inc_url, verify=True, headers=_get_headers(), timeout=30)
    # For unsuccesful request.
    if r.status_code != 200:
        logging.error(f"Status code error:{r.status_code}\n {inc_url}\n")
        return (-1.0, -1.0, -1.0, -1.0)

    soup = bs4.BeautifulSoup(r.text, "lxml")

    # Gets a list of bs4 tags that have these elements in them, then
    # uses list indexing to obtain the one that we need and then gets
    # the text for it. Removes commas, and the resulting number in str
    # form is converted to a float.
    rev20, rev19, ebit20, ebit19 = -1.0, -1.0, -1.0, -1.0
    index = 0
    for i, tag in enumerate(soup.select("div section span")):
        if tag.text == "Breakdown":
            index = i
        if "2020" in tag.text:
            offset20 = i - index
        if "2019" in tag.text:
            offset19 = i - index

        if tag.text == "Total Revenue":
            # 2020 revenue.
            try:
                rev20 = float(
                    soup.select("div section span")[i + offset20].text.replace(",", "")
                )
            except Exception:
                _log_error(inc_url, ticker, place="rev20")

            # 2019 revenue.
            try:
                rev19 = float(
                    soup.select("div section span")[i + offset19].text.replace(",", "")
                )
            except Exception:
                _log_error(inc_url, ticker, place="rev19")

        if tag.text == "EBIT":
            # 2020 EBIT.
            try:
                ebit20 = float(
                    soup.select("div section span")[i + offset20].text.replace(",", "")
                )
            except Exception:
                _log_error(inc_url, ticker, place="ebit20")

            # 2019 EBIT.
            try:
                ebit19 = float(
                    soup.select("div section span")[i + offset19].text.replace(",", "")
                )
            except Exception:
                _log_error(inc_url, ticker, place="ebit19")

    return (rev20, rev19, ebit20, ebit19)


def get_urls(ticker: str) -> Tuple[str, str, str]:
    """Generates the Yahoo finance URLs required in the rest of the scraper.
    
    Three Yahoo Finance URLs are generated, for the following webpages:
        historical price webpage
        balance sheet webpage
        income statement webpage

    Args:
        ticker (str): Official ticker of company as used on Yahoo Finance.

    Returns:
        Tuple[str, str, str]: Historical price webpage URL, balance sheet
            webpage URL, income statement webpage URL.
    """
    # Historical price is sourced from here.
    hist_price_url = f"https://finance.yahoo.com/quote/{ticker}/history?period1=1478131200&period2=1609372800&interval=1mo&filter=history&frequency=1mo&includeAdjustedClose=true"

    # debt and share number sourced from here.
    bal_sheet_url = f"https://finance.yahoo.com/quote/{ticker}/balance-sheet?p={ticker}"

    # All other metrics sourced from here.
    inc_stmt_url = f"https://finance.yahoo.com/quote/{ticker}/financials?p={ticker}"

    return (hist_price_url, bal_sheet_url, inc_stmt_url)


def get_hist_price(price_url: str, ticker: str) -> Tuple[float, float, float, float]:
    """Retrieves the historical price data for a company for 2017 to 2020.

    The price data recorded is the final closing price for Dec of each year.

    Args:
        price_url (str): Yahoo Finance URL for historical price webpage.
        ticker (str): Official ticker of company as used on Yahoo Finance.

    Returns:
        Tuple[float, float, float, float]: 2020 price, 2019 price, 2018 price,
            2017 price.
    """
    r = requests.get(price_url, verify=True, headers=_get_headers(), timeout=30)
    # For unsuccessful request.
    if r.status_code != 200:
        logging.error(f"Status code error:{r.status_code}\n {price_url}\n")
        return (-1.0, -1.0, -1.0, -1.0)

    element_html = lxml.html.fromstring(r.content)
    table = element_html.xpath("//table")
    table_tree = lxml.etree.tostring(table[0], method="xml")
    data = pd.read_html(table_tree)[0]
    mask = pd.to_numeric(data["Open"], errors="coerce").notnull()

    data1 = data[mask]
    data1.set_axis(list(range(len(data1))), inplace=True)

    price20, price19, price18, price17 = -1.0, -1.0, -1.0, -1.0
    # 2020 price.
    try:
        price20 = float(data1.loc[0, "Close*"])

    except Exception:
        _log_error(price_url, ticker, place="price20")

    # 2019 price.
    try:
        price19 = float(data1.loc[12, "Close*"])
    except Exception:
        _log_error(price_url, ticker, place="price19")

    # 2018 price.
    try:
        price18 = float(data1.loc[24, "Close*"])
    except Exception:
        _log_error(price_url, ticker, place="price18")

    # 2017 price.
    try:
        price17 = float(data1.loc[36, "Close*"])
    except Exception:
        _log_error(price_url, ticker, place="price17")

    return (price20, price19, price18, price17)


def _get_headers() -> Dict[str, str]:
    # Returns headers that allow you to scrape Yahoo finance.
    return {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image"
        "/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7",
        "cache-control": "max-age=0",
        "dnt": "1",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/"
        "537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
    }


def _log_error(url: str, ticker: str, place: str) -> None:
    logging.error(
        f"Scraping error: {place}\n"
        f"\tError: {sys.exc_info()[0]}\n"
        f"\turl: {url}\n"
        f"\tticker: {ticker}\n"
    )


if __name__ == "__main__":
    pass
