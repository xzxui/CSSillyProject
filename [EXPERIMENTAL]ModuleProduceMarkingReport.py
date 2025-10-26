import configs
import pydantic
import base64
import io
from PIL import Image
from time import time
import json

import ModuleLLMQuery

# This class is only for prompt engineering purpose,
# and the data stored in an instance of this class
# is not returned by this module in any way
class GradingPoint(pydantic.BaseModel):
    grading_point_type: str = pydantic.Field(..., description="the type of this grading point, which is usually the character/string before the number, e.g. the type of B1 is just B")
    marks_worth: int = pydantic.Field(..., description="the number of marks this grading point is worth. For example, a B2 is worth 2 marks while an M1 is worth 1")
    marks_earned: int = pydantic.Field(..., description="the number of marks the candidate earned")

class MarkedQuestion(pydantic.BaseModel):
    question_number: str = pydantic.Field(..., description="the question number, e.g. 3(a)(i), 3(a)(ii), 3(b), 4(a), 5, 6. do not write things like 3(a)(i and ii) or 3(a and b) as one Question, instead write them seperately as two")
    student_answer: str = pydantic.Field(..., description="the answer written by the student, which in some cases could be emtpy")
    guidance: str = pydantic.Field(..., description="the guidance on the marking scheme for the marking of this question")
    grading_points: list[GradingPoint] = pydantic.Field(..., description="The grading points (e.g. B1, B1, A1, M1, M2) included in the marking scheme of this question. Regardless of whether or not a grading point is earned by the candidate, it should be included in this list. If there are no grading points looking like B1, M1, A2 or A1 for this question, just leave this list empty.")
    max_marks: int = pydantic.Field(..., description="the number of marks this question is worth.")
    awarded_marks: int = pydantic.Field(..., description="the marks the student earns.")
    custom_error: str = pydantic.Field(..., description="leave empty unless you want to raise a fatal error, the details of which you shall specify here")

class Question(pydantic.BaseModel):
    question_number: str = pydantic.Field(..., description="the question number, e.g. 3(a)(i), 3(a)(ii), 3(b), 4(a), 5, 6.")
    page_nums_of_statement_of_the_problem_in_qp: list[int] = pydantic.Field(..., min_length=1, description="page numbers(must be consecutive, e.g. [1,2,3] and not [1,3]) of pages in the exam paper in which the statement of the problem(NOT always the same as the answer space!) is included, may be more than one")
    page_nums_of_answer_space_in_qp: list[int] = pydantic.Field(..., min_length=1, description="page numbers(must be consecutive, e.g. [1,2,3] and not [1,3]) of pages in the exam paper in which the space left for student to answer this question is included, may be more than one, these usually come after the description")
    page_nums_in_ms: list[int] = pydantic.Field(..., min_length=1, description="page numbers(must be consecutive, e.g. [1,2,3] and not [1,3]) of pages in the marking scheme in which the marking guidance of this question is included, may be more than one")
    #check_box: bool = pydantic.Field(..., description="Whether or not you've noticed the fact that the page numbers of the question description")

class BasicInformation(pydantic.BaseModel):
    syllabus_code: str = pydantic.Field(..., description="the 4-digit syllabus code shown at the top-right corner of the cover of the marking scheme, e.g. 9701/12 at the top-right of the cover => the syllabus code is 9701")
    component_number: str = pydantic.Field(..., description="the 2-digit component number shown at the top-right corner of the cover of the marking scheme, e.g. 9701/12 at the top-right of the cover => the component number is 12")
    questions: list[Question] = pydantic.Field(..., description="the list of question numbers presented in the exam paper(regardless of whether or not the question is answered by the candidate) in increasing order, e.g. 1(a), 1(b), 2, 3(a)(i), 3(a)(ii).  do not write things like 3(a)(i and ii) or 3(a and b) as one Question, instead write them seperately as two")
    custom_error: str = pydantic.Field(..., description="leave empty unless you want to raise a fatal error, the details of which you shall specify here")

class Feedback(pydantic.BaseModel):
    areas_of_strengths: str = pydantic.Field(..., description="a detailed comment on the areas where the student performed well")
    areas_for_improvement: str = pydantic.Field(..., description="a detailed comment on the areas where the student performed well")
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
    #with open("test_folder/tmp.png", "wb") as f:
    #    f.write(base64.b64decode(marking_scheme_b64imgs[-1]))
    #exit()
    print("Sending request to AI to fill the basic information, THIS MAY TAKE A WHILE")
    before=time()
    basic_information = ModuleLLMQuery.LLMQuery(
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
            {"role": "user", "content": "Now, please fill in some general information that you see in the exam paper and the marking scheme."},
        ],
        response_format=BasicInformation,
        model="gpt-5"
    )
    print(f"The AI responded, and it took {time()-before}s") # 
    # Allow the AI to handle edge cases
    if basic_information.custom_error:
        raise RuntimeError("The AI raised a fatal error!\n", basic_information.custom_error)
    print(basic_information)
    print("Now marking the questions, THIS MAY TAKE A WHILE")
    before=time()
    marked_questions = []
    for question in basic_information.questions:
        range_of_pgs_in_qp = range(min(question.page_nums_of_statement_of_the_problem_in_qp)-1, max(question.page_nums_of_answer_space_in_qp))
        range_of_pgs_in_ms = range(min(question.page_nums_in_ms)-1, max(question.page_nums_in_ms))
        marked_questions.append(ModuleLLMQuery.LLMQuery(
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
                *generate_image_conversation(student_work_b64imgs, "the exam paper that the candidate has written", range_of_pages=range_of_pgs_in_qp),
                *generate_image_conversation(marking_scheme_b64imgs, "the marking scheme", range_of_pages=range_of_pgs_in_ms),
                {"role": "user", "content": f"Now, please mark question {question}. Remember to follow the guidance on the marking scheme"},
            ],
            response_format=MarkedQuestion,
            model="gpt-5-mini"
        ))
        # Allow the AI to handle edge cases
        if marked_questions[-1].custom_error:
            raise RuntimeError("The AI raised a fatal error!\n", marked_questions[-1].custom_error)
        if print_marking_report:
            print(
                f"question_number:\t{marked_questions[-1].question_number}\n"
                f"student_answer:\t{marked_questions[-1].student_answer}\n"
                f"guidance:\t{marked_questions[-1].guidance}\n"
                f"max_marks:\t{marked_questions[-1].max_marks}\n"
                f"awarded_marks:\t{marked_questions[-1].awarded_marks}\n"
                f"grading_points:"
            )
            print("\t", " ".join([f"{marks_earned}/{grading_point.grading_point_type+str(marks_worth)}" for grading_point in marked_questions[-1].grading_points]))
            print()
    print(f"Done marking the questions, and it took {time()-before}s")
    print("Now requesting the AI to write feedback")
    before=time()
    feedback = LLMQuery(
        [
            {
                "role": "system",
                "content": (
                    "You are a responsible and experienced teacher who is giving comments on a student's performance in a recent exam.\n"
                    "The user, who is your co-worker who has marked the student's exam, will provide you the marked questions of this student.\n"
                )
            },
            {
                "role": "user",
                "content": (
                    "Basic Information of Exam: "+json.dumps(basic_information, indent=4)+\
                    "The Marked Questions: "+json.dumps(marked_questions, indent=4)
                )
            }
        ],
        response_format=Feedback
    )
    print(f"Done writting the feedbacks, and it took {time()-before}s")
    # Allow the AI to handle edge cases
    if feedback.custom_error:
        raise RuntimeError("The AI raised a fatal error!\n", feedback.custom_error)
    return basic_information.syllabus_code,\
           basic_information.component_number,\
           [[question.question_number, question.max_marks, question.awarded_marks] for question in marked_questions],\
           feedback.areas_of_strengths,\
           feedback.areas_for_improvement

def generate_image_conversation(b64_imgs, name_of_pdf, range_of_pages=None):
    # Generate 'messages' in order to let the AI see all the pages in the right ORDER
    conversation = []
    if not range_of_pages:
        range_of_pages = range(len(name_of_pdf))
    idx = range_of_pages.start
    for b64_img in b64_imgs[range_of_pages.start : range_of_pages.stop]:
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
    student_work_path = "test_folder/data/9709_12_2024_MayJune_Mathematics_qp_with_less_answers.pdf"
    mark_scheme_path = "test_folder/data/9709_12_2024_MayJune_Mathematics_ms.pdf"
    
    # Convert to base 64 images
    print("Converting to base 64.")
    completed_question_paper_b64s = ModulePDF2b64s.PDF2b64s(student_work_path)
    mark_scheme_b64s = ModulePDF2b64s.PDF2b64s(mark_scheme_path)
    print("Converting done, marking now.")

    # Mark the Paper
    syllabus_code, component_num, marking_report, strengths, weaknesses = ProduceMarkingReport(completed_question_paper_b64s, mark_scheme_b64s)
    print("\nAll marking done.")
