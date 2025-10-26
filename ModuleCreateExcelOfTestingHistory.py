import configs
import openpyxl
from pathlib import Path

def CreateExcelOfTestingHistory():
    """
    Args:
        No arguments
    Return:
        No return
    Process:
        Create an excel file about the student's testing history, showing the score and grade achieved in each paper, and the AI's comment on the performance of the student, and save to configs.path_to_excel_of_testing_history. Notice that the path of the folder containing all the student's practice paper history is stored in configs.marking_result_folder. Every single file ending with 'xlsx' under that folder should be a marking result save.
    """
    wb = openpyxl.Workbook()
    ws = wb.active

    xlsx_files = Path(configs.marking_result_folder).glob('*.xlsx')

    rows = [[]]
    for file_path in xlsx_files:
        print(f"Reading: {file_path}")
        new, first = DetermineRowsToAdd(file_path)
        rows.append(new)
    rows[0] = first
    for row in rows:
        ws.append(row)
    print(f"Added a total of {len(rows)} rows")

    wb.save(configs.path_to_excel_of_testing_history)
    print(f"Excel of testing history saved to {configs.path_to_excel_of_testing_history}")

def DetermineRowsToAdd(path_to_excel, start_col=9, end_col=15):
    wb_obj = openpyxl.load_workbook(path_to_excel)
    sheet_obj = wb_obj.active
    new_row = []
    override_row = []
    for col in range(start_col, end_col+1):
        new_row.append(sheet_obj.cell(row=2, column=col).value)
        override_row.append(sheet_obj.cell(row=1, column=col).value)
    return new_row, override_row

if __name__ == "__main__":
    CreateExcelOfTestingHistory()
