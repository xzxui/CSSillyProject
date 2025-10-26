import configs
import pydantic
import base64
import io
from PIL import Image
from time import time

import ModuleLLMQuery

class GradingPoint(pydantic.BaseModel):
    grading_point_type: str = pydantic.Field(..., description="the type of this grading point, which is usually the character/string before the number, e.g. the type of B1 is just B")
    #guidance: str = pydantic.Field(..., description="the guidance given by the marking scheme for this grading point")
    marks_worth: int = pydantic.Field(..., description="the number of marks this grading point is worth. For example, a B2 is worth 2 marks while an M1 is worth 1")
    marks_earned: int = pydantic.Field(..., description="the number of marks the candidate earned")

class Question(pydantic.BaseModel):
    question_number: str = pydantic.Field(..., description="the question number, e.g. 3(a)(i), 3(a)(ii), 3(b), 4(a), 5, 6. do not write things like 3(a)(i and ii) or 3(a and b) as one Question, instead write them seperately as two")
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

def ProduceMarkingReport(student_work_b64imgs, marking_scheme_b64imgs):
    # Only for testing
    import random
    a=random.randint(1, 10)
    aa=random.randint(1, a)
    b=random.randint(1, 10)
    ba=random.randint(1, b)
    return("9709", "12", [["1(a)", a, aa], ["1(b)", b, ba]], "Too smart a monkey to receive such a score", "Too dumb a human to perform so poor") # for testing
    """
    Args:
        1. student_work_b64imgs: A list of strings(each string being a base 64 image)
        2. marking_scheme_b64imgs: A list of strings(each string being a base 64 image)
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
    print("Sending request to AI for marking, THIS MAY TAKE A WHILE")
    marking_report = ModuleLLMQuery.LLMQuery(
        [
            {"role": "system", "content": "You are an experienced A-Level examiner. You are marking the exam paper of a candidate. You will follow the instructions of the marking scheme when marking the exam paper. The user is your co-worker, and will provide you with the exam paper and the marking scheme."},
            {"role": "user", "content": [
                {
                    "type": "text",
                    "text": "Here is the "
                },
            ]},
            *generate_image_conversation(student_work_b64imgs, "the exam paper that the candidate has written"),
            *generate_image_conversation(marking_scheme_b64imgs, "the marking scheme"),
            {"role": "user", "content": "I have given you all the pages of the question paper that the candidate has submitted, as well as all the pages of the marking scheme. Remember, always follow the instructions on the marking scheme to give marks. Now, please start marking the candidate's work."},
        ],
        response_format=MarkingReport
    )
    if marking_report.custom_error:
        raise RuntimeError("The AI raised a fatal error!\n", marking_report.custom_error)
    print(marking_report)
    print(f"The AI responded, and it took {time()-a}s")

    return marking_report.syllabus_code, marking_report.component_number, [[question.question_number, question.max_marks, question.awarded_marks] for question in marking_report.questions], marking_report.strengths, marking_report.weaknesses

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

if __name__ == "__main__":
    import ModulePDF2b64s
    marking_scheme_b64imgs = ModulePDF2b64s.PDF2b64s("test_folder/data/9709_12_2024_MayJune_Mathematics_ms.pdf")
    a=time()
    print("Request sent.")
    marking_report = ModuleLLMQuery.LLMQuery(
        [
            {"role": "system", "content": "The user will give you a marking scheme in pdf, and you must tell the user the marking scheme for question 8(a) and 8(b) in details."},
            {"role": "user", "content": [
                {
                    "type": "text",
                    "text": "Here is the marking scheme."
                },
            ]},
            *generate_image_conversation(marking_scheme_b64imgs, "the marking scheme"),
        ],
    )
    print(marking_report)
    print(f"They responded in {time()-a}s")

