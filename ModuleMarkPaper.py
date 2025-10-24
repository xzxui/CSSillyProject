import configs
from ModulePDF2b64s import PDF2b64s
from ModuleProduceMarkingReport import ProduceMarkingReport
from ModuleFindGrade import FindGrade
from ModuleSaveMarkingResultToExcel import SaveMarkingResultToExcel

def MarkPaper(student_work_path, mark_scheme_path, threshold_table_path):
    """
    Args:
        1. student_work_path (<class 'str'>): path to a completed question paper pdf
        2. mark_scheme_path (<class 'str'>): path to a mark scheme pdf
        3. threshold_table_path (<class 'str'>): path to a threshold table pdf
    Return: No return
    Process:
        Follow the procedures below:
            1. Use ModulePDF2b64s.PDF2b64s to convert the pdf files containing student work, mark scheme, and threshold table each to a list of images. Each of the images should be in <class 'str'>, because they are in the form of base 64.
            2. Call ModuleProduceMarkingReport.ProduceMarkingReport
            3. Call ModuleFindGrade.FindGrade
            4. Call ModuleSaveMarkingResultToExcel.SaveMarkingResultToExcel
    """
    pass
