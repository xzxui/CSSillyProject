import configs

def CreateExcelOfTestingHistory():
    """
    Args:
        No arguments
    Return:
        No return
    Process:
        Create an excel file about the student's testing history, showing the score and grade achieved in each paper, and the AI's comment on the performance of the student. Notice that the path of the folder containing all the student's practice paper history is stored in configs.marking_result_folder. Every single file ending with 'xlsx' under that folder should be a marking result save.
    """
