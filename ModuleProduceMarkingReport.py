import configs
import pydantic
import base64
import io
from PIL import Image
from time import time

import ModuleLLMQuery

# This class is only for prompt engineering purpose,
# and the data stored in an instance of this class
# is not returned by this module in any way
class GradingPoint(pydantic.BaseModel):
    grading_point_type: str = pydantic.Field(..., description="the type of this grading point, which is usually the character/string before the number, e.g. the type of B1 is just B")
    marks_worth: int = pydantic.Field(..., description="the number of marks this grading point is worth. For example, a B2 is worth 2 marks while an M1 is worth 1")
    marks_earned: int = pydantic.Field(..., description="the number of marks the candidate earned")

class Question(pydantic.BaseModel):
    question_number: str = pydantic.Field(..., description="the question number, e.g. 3(a)(i), 3(a)(ii), 3(b), 4(a), 5, 6. do not write things like 3(a)(i and ii) or 3(a and b) as one Question, instead write them seperately as two")
    #candidate_answer: str = pydantic.Field(..., description="the answer given by the candidate")
    #marking_guidance: str = pydantic.Field(..., description="the guidance for marking shown on the marking scheme")
    marking_note: str = pydantic.Field(..., description="1.what did the candidate write? 2.what are the guidances given in the marking scheme? 3.do they align?")
    grading_points: list[GradingPoint] = pydantic.Field(..., description="The grading points (e.g. B1, B1, A1, M1, M2) included in the marking scheme of this question. Regardless of whether or not a grading point is earned by the candidate, it should be included in this list. If there are no grading points looking like B1, M1, A2 or A1 for this question, just leave this list empty.")
    max_marks: int = pydantic.Field(..., description="the maximum marks designed for this question.")
    awarded_marks: int = pydantic.Field(..., description="the marks the student earned.")

class MarkingReport(pydantic.BaseModel):
    syllabus_code: str = pydantic.Field(..., description="the 4-digit syllabus code shown at the top-right corner of the cover of the marking scheme, e.g. 9701/12 at the top-right of the cover => the syllabus code is 9701")
    component_number: str = pydantic.Field(..., description="the 2-digit component number shown at the top-right corner of the cover of the marking scheme, e.g. 9701/12 at the top-right of the cover => the component number is 12")
    questions: list[Question] = pydantic.Field(..., description="the list of the marked questions")
    strengths: str = pydantic.Field(..., description="skills that the candiate seems to master")
    weaknesses: str = pydantic.Field(..., description="skills that the candidate seems to lack")
    custom_error: str = pydantic.Field(..., description="leave empty unless you want to raise a fatal error, the details of which you shall specify here")

def ProduceMarkingReport(student_work_b64imgs, marking_scheme_b64imgs, print_marking_report=False):
    # Only for debugging
    """
    import random
    a=random.randint(1, 10)
    aa=random.randint(1, a)
    b=random.randint(1, 10)
    ba=random.randint(1, b)
    return("9709", "12", [["1(a)", a, aa], ["1(b)", b, ba]], "Too smart a monkey to receive such a score", "Too dumb a human to perform so poor") # for testing
    """
    """
    Args:
        1. student_work_b64imgs: A list of strings(each string being a base 64 image)
        2. marking_scheme_b64imgs: A list of strings(each string being a base 64 image)
        3. print_marking_report: whether to print the marking report given by the AI
    Return:
        1. Syllabus code (<class 'str'>)
        2. Component number (<class 'str'>
        3. A marking report, which is a 3xn (3 rows, n cols) 2D list, where the first column includes quesion numbers, the second column includes Maximum mark possible to be awarded to the question, and the third column includes the marks the student received, e.g. [["3(a)", 10, 9], ["3(b)", 7, 6], ["4", 7, 7]]
        4. A comment on strengths of the student
        5. A comment on weaknesses of the student
    Process:
        Call ModuleLLMQuery.LLMQuery to let the AI mark the student's paper
    """
    a=time()
    #with open("test_folder/tmp.png", "wb") as f:
    #    f.write(base64.b64decode(marking_scheme_b64imgs[-1]))
    #exit()
    print("Sending request to AI for marking, THIS MAY TAKE A WHILE(~5 to 10 minutes), timestamp:", time())
    marking_report = ModuleLLMQuery.LLMQuery(
        [
            {
                "role": "system",
                "content": (
                    "You are an experienced A-Level examiner.\n"
                    "You are marking the exam paper of a candidate.\n"
                    "You will follow the instructions of the marking scheme when marking the exam paper.\n"
                    "The user is your co-worker, and will provide you with the exam paper and the marking scheme.\n"
                )
            },
            *generate_image_conversation(student_work_b64imgs, "the exam paper that the candidate has written"),
            *generate_image_conversation(marking_scheme_b64imgs, "the marking scheme"),
            {"role": "user", "content": "I have given you all the pages of the question paper that the candidate has submitted, as well as all the pages of the marking scheme. Remember, always follow the instructions on the marking scheme to give marks. Now, please start marking the candidate's work."},
        ],
        response_format=MarkingReport,
        model="o4-mini"
    )
    # Allow the AI to handle edge cases
    if marking_report.custom_error:
        raise RuntimeError("The AI raised a fatal error!\n", marking_report.custom_error)
    print(f"The AI responded, and it took {time()-a}s")
    #print(marking_report)
    if print_marking_report:
        for marked_question in marking_report.questions:
            print(
                f"question_number:\t{marked_question.question_number}\n"
                #f"student_answer:\t{marked_question.candidate_answer}\n"
                #f"marking guidance:\t{marked_question.marking_guidance}\n"
                f"marking note:\t{marked_question.marking_note}\n"
                f"max_marks:\t{marked_question.max_marks}\n"
                f"awarded_marks:\t{marked_question.awarded_marks}\n"
                f"grading_points:"
            )
            print("\t", " ".join([f"{grading_point.marks_earned}/{grading_point.grading_point_type+str(grading_point.marks_worth)}" for grading_point in marked_question.grading_points]))

    return marking_report.syllabus_code, marking_report.component_number, [[question.question_number, question.max_marks, question.awarded_marks] for question in marking_report.questions], marking_report.strengths, marking_report.weaknesses

def generate_image_conversation(b64_imgs, name_of_pdf):
    # Generate 'messages' in order to let the AI see all the pages in the right ORDER
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

if __name__ == "__main__":
    import ModulePDF2b64s
    student_work_paths =[
        "test_folder/data/9709_12_2024_MayJune_Mathematics_qp_first_try.pdf",
        "test_folder/data/9709_12_2024_MayJune_Mathematics_qp_second_try.pdf",
    ]
    mark_scheme_paths = [
        "test_folder/data/9709_12_2024_MayJune_Mathematics_ms.pdf",
        "test_folder/data/9709_12_2024_MayJune_Mathematics_ms.pdf",
    ]
    for idx in range(len(mark_scheme_paths)):
        student_work_path = student_work_paths[idx]
        mark_scheme_path = mark_scheme_paths[idx]
        # Convert to base 64 images
        print("Converting to base 64.")
        completed_question_paper_b64s = ModulePDF2b64s.PDF2b64s(student_work_path)
        mark_scheme_b64s = ModulePDF2b64s.PDF2b64s(mark_scheme_path)
        print("Converting done, marking now.")

        # Mark the Paper
        syllabus_code, component_num, marking_report, strengths, weaknesses = ProduceMarkingReport(completed_question_paper_b64s, mark_scheme_b64s, print_marking_report=True)
        print("\nAll marking done.\n")

