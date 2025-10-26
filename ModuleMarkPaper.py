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
    Return:
        1. of <class 'int'> the total marks the student earned
        2. of <class 'int'> the total marks available on the question paper
        3. of <class 'str'> the grade
        4. of <class 'str'> the positive comment
        5. of <class 'str'> the negative comment
    Process:
        Follow the procedures below:
            1. Use ModulePDF2b64s.PDF2b64s to convert the pdf files containing student work, mark scheme, and threshold table each to a list of images. Each of the images should be in <class 'str'>, because they are in the form of base 64.
            2. Call ModuleProduceMarkingReport.ProduceMarkingReport
            3. Call ModuleFindGrade.FindGrade
            4. Call ModuleSaveMarkingResultToExcel.SaveMarkingResultToExcel
    """
    # Convert to base 64 images
    print("Converting to base 64.")
    completed_question_paper_b64s = ModulePDF2b64s.PDF2b64s(student_work_path)
    mark_scheme_b64s = ModulePDF2b64s.PDF2b64s(mark_scheme_path)
    threshold_table_b64s = ModulePDF2b64s.PDF2b64s(threshold_table_path)
    print("Converting done, marking now.")

    # Mark the Paper
    syllabus_code, component_num, marking_report, strengths, weaknesses = ModuleProduceMarkingReport.ProduceMarkingReport(completed_question_paper_b64s, mark_scheme_b64s)
    print("Marking done, grading now.")
    # Grade the Paper
    marks_earned, marks_there, grade = ModuleFindGrade.FindGrade(component_num, marking_report, threshold_table_b64s)
    print("Grading done, saving now.")
    # Save the Result
    ModuleSaveMarkingResultToExcel.SaveMarkingResultToExcel(os.path.splitext(configs.marking_result_folder+os.path.basename(student_work_path))[0]+".xlsx", syllabus_code, component_num, marking_report, strengths, weaknesses, marks_earned, marks_there, grade)
    print("Saving done!")

    return marks_earned, marks_there, grade, strengths, weaknesses

if __name__ == "__main__":
    score, score_there, grade, positive, negative = MarkPaper("test_folder/data/9709_12_2024_MayJune_Mathematics_qp_with_less_answers.pdf", "test_folder/data/9709_12_2024_MayJune_Mathematics_ms.pdf", "test_folder/data/9709_12_2024_MayJune_Mathematics_tt.pdf")
    score, score_there, grade, positive, negative = MarkPaper("test_folder/data/9709_12_2024_MayJune_Mathematics_qp.pdf", "test_folder/data/9709_12_2024_MayJune_Mathematics_ms.pdf", "test_folder/data/9709_12_2024_MayJune_Mathematics_tt.pdf")
    print(
        f"Total Score: \t{score}\n"
        f"Score There: \t{score_there}\n"
        f"Grade Earned: \t{grade}\n"
        f"Strengths: \t{positive}\n"
        f"Weaknesses: \t{negative}\n"
    )
    print("No fatal error occured. Please go and check the excel file outputted by ModuleSaveMarkingResultToExcel, which should be under {configs.student_work_path}")
