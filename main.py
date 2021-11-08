"""Main scraper script to run"""


import functions
import numpy as np
import pandas as pd


def main() -> None:
    # Enable logging.
    functions.configure_logs()

    # Correctly format the skeleton Excel table before use.
    functions.fix_ticker_formatting(
        filename = 'original_data.xlsx',
        save_filename = 'ready_input_data.xlsx',
        column = 'A') 

    data_file: str = 'ready_input_data.xlsx' # Formatted table.
    input_df = pd.read_excel(data_file)

    work_df = input_df.copy() # To avoid working with original df.

    print('Status: Starting webscrape.\n')
    for i in range(len(work_df)):
        ticker: str = work_df['Ticker'][i]
        print(f'\tStatus: #{i} Currently scraping data: {ticker}\n')

        # Getting the url's for a ticker.
        price_url, bal_url, inc_url = functions.get_urls(ticker)
        
        # Getting the data for a ticker.
        price20, price19 = functions.get_hist_price(price_url, ticker)
        shares20, shares19, debt20, debt19 = functions.get_debt_shares(bal_url, ticker)
        rev20, rev19, ebit20, ebit19 = functions.get_revenue_ebit(inc_url, ticker)
        
        # Entering data into dataframe.
        work_df.loc[i, 'Stock Price 2020'] = price20
        work_df.loc[i, 'Stock Price 2019'] = price19
        work_df.loc[i, 'Revenue 2020'] = rev20
        work_df.loc[i, 'Revenue 2019'] = rev19
        work_df.loc[i, 'Share Number 2020'] = shares20
        work_df.loc[i, 'Share Number 2019'] = shares19
        work_df.loc[i, 'Debt 2020'] = debt20
        work_df.loc[i, 'Debt 2019'] = debt19
        work_df.loc[i, 'EBIT 2020'] = ebit20
        work_df.loc[i, 'EBIT 2019'] = ebit19

    # Export scraped data to Excel file.
    work_df.replace(to_replace = -1, value = np.nan)
    work_df.to_excel('output_data.xlsx')
    print('Status: Data exported!\nAll done!')


if __name__ == '__main__':
    main()