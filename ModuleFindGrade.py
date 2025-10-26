import configs
import pydantic
import ModuleLLMQuery
import time

class Grade(pydantic.BaseModel):
    grade_received: str = pydantic.Field(..., min_length=1, max_length=1)
    custom_error: str = pydantic.Field(..., description="leave empty unless there is a fatal error, the details of which you shall specify here")

def FindGrade(component_number, marking_report, grading_threshold_table_b64imgs):
    """
    Args:
        1. component_number (<class 'num'>)
        2. marking_report (<class 'list'>): a marking report, which is a 3xn (3 rows, n cols) 2D list, where the first column includes quesion numbers, the second column includes Maximum mark possible to be awarded to the question, and the third column includes the marks the student received, e.g. [["3(a)", 10, 9], ["3(b)", 7, 6], ["4", 7, 7]]
        3. grading_threshold_table_b64imgs (<class 'list'>): A list of strings(each string being a base 64 image)
    Return:
        1. of <class 'int'> the total marks earned
        2. of <class 'int'> the total marks available
        3. of <class 'str'> the grade like 'A', 'B', or 'C'
    Process:
        Ask the AI to read the grading threshold table for us, and use the marking report and the parsed grading threshold table to determine the grade
    """
    total_raw_marks = calculate_total_score(marking_report)
    total_marks_there = calculate_total_score(marking_report, cal_total_avail=True)
    print("Sending request to AI for finding grade")
    before = time.time()
    grade = ModuleLLMQuery.LLMQuery(
        [
            {"role": "system", "content": "Your job is to look up a table in order to match the score an exam candidate score to their grade. The user will give you a grading threshold table containing information required to do this, as well as the component number of the paper the candidate took and their score received. If the grade the student received passes none of the thresholds in the table, simply award an 'U'"},
            *generate_image_conversation(grading_threshold_table_b64imgs, "the grading threshold table"),
            {"role": "user", "content": f"The score the candidate received for component {component_number} is {total_raw_marks}. Now, please use the table to find the grade of the student"}
        ],
        response_format=Grade,
        model="gpt-5-mini",
    )
    print(f"The AI responded in {time.time()-before}s")
    if grade.custom_error:
        raise RuntimeError("The AI raised a fatal error!\n", grade.custom_error)
    return total_raw_marks, total_marks_there, grade.grade_received

# This is copied from ModuleProduceMarkingReport.py, and it is defined twice instead of imported from one module because they might be modified seperately in futural development
def generate_image_conversation(b64_imgs, name_of_pdf):
    conversation = []
    idx = 0
    for b64_img in b64_imgs:
        idx += 1
        conversation.extend([
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"This is page {idx}/{len(b64_imgs)} of {name_of_pdf}."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/{configs.img_extension};base64,{b64_img}"
                        }
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": f"I see, this is page {idx} of {name_of_pdf}."}
                ]
            }
        ])
    return conversation

def calculate_total_score(marking_report, cal_total_avail=False):
    total_scores = 0
    for question_number, marks_worth, marks_earned in marking_report:
        if cal_total_avail:
            total_scores += marks_worth
        else:
            total_scores += marks_earned
    return total_scores

if __name__ == "__main__":
    import ModuleProduceMarkingReport, ModulePDF2b64s, time
    def calculate_correct_grade(total_score, thresholds):
        received_grade = 'U'
        for threshold, grade in thresholds:
            if total_score >= threshold:
                received_grade = grade
                break
        return received_grade
    tests_to_run = [
        [
            "12",
            [
                ['1', 3, 1], ['2', 5, 5], ['3(a)', 3, 3], ['3(b)', 3, 3], ['4(a)', 1, 1], ['4(b)', 2, 2], ['4(c)', 4, 4], ['5(a)', 4, 4], ['5(b)(i)', 2, 2], ['5(b)(ii)', 3, 3], ['6(a)', 4, 4], ['6(b)', 5, 5], ['7(a)', 5, 5], ['7(b)', 3, 3], ['8(a)(i)', 2, 2], ['8(a)(ii)', 4, 4], ['8(b)', 4, 3], ['9(a)', 4, 3], ['9(b)', 4, 4], ['10(a)', 4, 4], ['10(b)', 6, 4]
            ],
            [[60, 'A'], [49, 'B'], [36, 'C'], [24, 'D'], [12, 'E']],
            ModulePDF2b64s.PDF2b64s("test_folder/data/9709_12_2024_MayJune_Mathematics_tt.pdf")
        ],
        [
            "11",
            [
                ['1', 3, 0],
                ['2(a)(i)', 3, 11]
            ],
            [[50, 'A'], [44, 'B'], [34, 'C'], [23, 'D'], [12, 'E']],
            ModulePDF2b64s.PDF2b64s("test_folder/data/9709_12_2024_MayJune_Mathematics_tt.pdf")
        ],
        [
            "63",
            [
                ['1', 3, 18],
                ['2', 4, 0]
            ],
            [[42, 'A'], [36, 'B'], [30, 'C'], [24, 'D'], [18, 'E']],
            ModulePDF2b64s.PDF2b64s("test_folder/data/9709_12_2024_MayJune_Mathematics_tt.pdf")
        ],


    ]
    idx = 0
    success_count = 0
    total_seconds = 0
    for component_number, marking_report, threshold_table, b64_threshold_table in tests_to_run:
        idx += 1
        total_score = calculate_total_score(marking_report)
        correct = calculate_correct_grade(total_score, threshold_table)
        before = time.time()
        attempt = FindGrade(component_number, marking_report, b64_threshold_table)
        seconds_taken = time.time()-before
        total_seconds += seconds_taken
        if attempt == correct:
            print(f"Test {idx}/{len(tests_to_run)}\tPASSED and took {seconds_taken}s.")
            success_count += 1
        else:
            print(f"!!!Test {idx}/{len(tests_to_run)}\tFAILED and took {seconds_taken}s.")
            print(f"Should be {correct}, got {attempt}")
            print(f"Correct total score: {total_score}")
            print(f"Correct thresholds: {threshold_table}")
    print()
    print(f"Successes {success_count}/{len(tests_to_run)}, \von average each took {total_seconds/len(tests_to_run)}s.")
