import configs
from ModuleLLMQuery import LLMQuery

def FindGrade(marking_report, grading_threshold_table_b64imgs):
    """
    Args:
        1. marking_report (<class 'list'>): a marking report, which is a 3xn (3 rows, n cols) 2D list, where the first column includes quesion numbers, the second column includes Maximum mark possible to be awarded to the question, and the third column includes the marks the student received, e.g. [["3(a)", 10, 9], ["3(b)", 7, 6], ["4", 7, 7]]
        2. grading_threshold_table_b64imgs (<class 'list'>): A list of strings(each string being a base 64 image)
    Return:
        A grade like 'A', 'B', or 'C'
    Process:
        Ask the AI to read the grading threshold table for us, and use the marking report and the parsed grading threshold table to determine the grade
    """
    pass
