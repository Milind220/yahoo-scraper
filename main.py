"""Main scraper script to run"""


import numpy as np
import pandas as pd

import functions


def main() -> None:
    # Enable logging.
    functions.configure_logs()

    # Correctly format the skeleton Excel table before use.
    functions.fix_ticker_formatting(
        filename = 'original_data.xlsx',
        save_filename = 'ready_input_data.xlsx',
        column = 'A')

    data_file: str = 'ready_input_data' # Formatted table.
    input_df = pd.read_excel(data_file)

    work_df = input_df.copy() # To avoid working with original df.

    df_length = len(work_df)
    print('Status: Starting webscrape.\n')
    for i in range(df_length):
        ticker: str = work_df['Ticker'][i]
        print(f'\tStatus: # {i+1}/{df_length} Currently scraping data: {ticker}\n')

        # Getting the url's for a ticker.
        price_url, bal_url, inc_url = functions.get_urls(ticker)

        # Getting the data for a ticker.
        price20, price19, price18, price17 = functions.get_hist_price(price_url, ticker)
        functions.generate_rand_delay()
        shares20, shares19, debt20, debt19 = functions.get_debt_shares(bal_url, ticker)
        functions.generate_rand_delay()
        rev20, rev19, ebit20, ebit19 = functions.get_revenue_ebit(inc_url, ticker)
        functions.generate_rand_delay()

        # Entering data into dataframe.
        work_df.loc[i, 'Price 2020'] = price20
        work_df.loc[i, 'Price 2019'] = price19
        work_df.loc[i, 'Price 2018'] = price18
        work_df.loc[i, 'Price 2017'] = price17
        work_df.loc[i, 'Revenue 2020'] = rev20
        work_df.loc[i, 'Revenue 2019'] = rev19
        work_df.loc[i, 'Share Number 2020'] = shares20
        work_df.loc[i, 'Share Number 2019'] = shares19
        work_df.loc[i, 'Debt 2020'] = debt20
        work_df.loc[i, 'Debt 2019'] = debt19
        work_df.loc[i, 'EBIT 2020'] = ebit20
        work_df.loc[i, 'EBIT 2019'] = ebit19

    # Export scraped data to Excel file.

    work_df.replace(to_replace = -1.0, value = np.nan)
    _file_name: str = str(input('\nWhat filename to save as?'
                          '\n1. Use a unique filename!'
                          '\n2. Don\'t provide a file extension'
                          '\nEnter here: '))
    work_df.to_excel(f'{_file_name}.xlsx')
    print('Status: Data exported!\nAll done!')


if __name__ == '__main__':
    main()
