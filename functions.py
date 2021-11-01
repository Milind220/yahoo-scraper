import openpyxl


def col_dots_not_dashes(filename: str,
                    save_filename: str,
                    column: str) -> None:
    workbook = openpyxl.load_workbook(filename=filename)
    ws = workbook.active # Opens the workbook.

    col = ws[column]
    for cell in col:
        cell.value = '.'.join(cell.value.split('-'))
        # This replaces the - in the ticker with a .
    
    workbook.save(filename=save_filename)


if __name__ == '__main__':
    col_dots_not_dashes(filename='data_1.xlsx', save_filename='data_2.xlsx', column='A')