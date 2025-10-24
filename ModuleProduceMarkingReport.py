import configs

def ProduceMarkingReport(student_work_b64imgs, mark_scheme_b64imgs):
    """
    Args:
        1. student_work_b64imgs: A list of strings(each string being a base 64 image)
        2. mark_scheme_b64imgs: A list of strings(each string being a base 64 image)
    Return:
        A marking report, which is a 3xn (3 rows, n cols) 2D list, where the first column includes quesion numbers, the second column includes Maximum mark possible to be awarded to the question, and the third column includes the marks the student received, e.g. [["3(a)", 10, 9], ["3(b)", 7, 6], ["4", 7, 7]]
    Process:
        Call ModuleLLMQuery.LLMQuery to let the AI mark the student's paper
    """
    pass
