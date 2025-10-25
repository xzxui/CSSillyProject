import configs
import ModulePDF2b64s
import ModuleProduceMarkingReport
import ModuleFindGrade
import ModuleSaveMarkingResultToExcel
import os

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
    completed_question_paper_b64s = ModulePDF2b64s.PDF2b64s(student_work_path)
    mark_scheme_b64s = ModulePDF2b64s.PDF2b64s(mark_scheme_path)
    threshold_table_b64s = ModulePDF2b64s.PDF2b64s(threshold_table_path)
    syllabus_code, component_num, marking_report, strengths, weaknesses = ModuleProduceMarkingReport.ProduceMarkingReport(completed_question_paper_b64s, mark_scheme_b64s)
    grade = ModuleFindGrade.FindGrade(component_num, marking_report, threshold_table_b64s)
    ModuleSaveMarkingResultToExcel.SaveMarkingResultToExcel(configs.marking_result_folder+os.path.basename(student_work_path), syllabus_code, component_num, marking_report, strengths, weaknesses, grade)

if __name__ == "__main__":
    print(MarkPaper("test_folder/data/9709_12_2024_MayJune_Mathematics_qp.pdf", "test_folder/data/9709_12_2024_MayJune_Mathematics_ms.pdf", "test_folder/data/9709_12_2024_MayJune_Mathematics_tt.pdf"))
    print("No fatal error occured. Please go and check the excel file outputted by ModuleSaveMarkingResultToExcel, which should be under {configs.student_work_path}")
