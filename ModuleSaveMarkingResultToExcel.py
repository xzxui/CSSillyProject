import configs

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
    pass
