import configs
import pandas as pd

def SaveMarkingResultToExcel(save_path, syllabus_code, component_number, marking_report, strengths, weaknesses, score, grade):
    """
    Args:
        1. save_path (<class 'str'>): the path of the excel file to save to
        2. syllabus_code (<class 'str'>)
        3. component_number (<class 'str'>)
        4. marking_report (<class 'list'>): the marking report
        5. strengths (<class 'str'>): the AI's comment on areas the student did well
        6. weaknesses (<class 'boolean'>): the AI's comment on areas the student did bad
        7. score (<class 'int'>)
        8. grade (<class 'str'>): the grade received, e.g. A, B, C, D, E, U
    Return: No return
    Process:
        Save the marking result into an excel file, and call ModuleCreateExcelOfTestingHistory.CreateExcelOfTestingHistory
    """
    Marking_report_columns = ['Question Number', 'Maximum Mark Possible', 'Marks Received']
    df_report = pd.DataFrame(marking_report, columns= Marking_report_columns)
    df_paper = pd.DataFrame({'Syllabus Code': [syllabus_code], 'Component Number': [component_number]})
    df_feekback = pd.DataFrame({'Weaknesses': [weaknesses], 'Strengths': [strengths]})
    df_result = pd.DataFrame({'Score':[score], 'Grade':[grade]})

    df_sheet=pd.concat([df_paper, df_report,df_result, df_feekback], axis=1)
    with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
        df_sheet.to_excel(writer, sheet_name='Marking Report', index=False)
    pass
#testcode: SaveMarkingResultToExcel('test_folder\\1.xlsx','syllabus', 'component' ,  [['1', 5, 4], ['2(a)', 10, 4], ['2(b)(i)', 5,4], ['2(b)(ii)',5,5]] , 'good', 'bad',114,514)