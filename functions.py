import openpyxl


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
        
        cell.value = '.'.join(ticker_data) # Adding the . while joining them
    workbook.save(filename=save_filename)


if __name__ == '__main__':
    pass