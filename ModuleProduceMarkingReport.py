import configs
import pydantic
import base64
import io
from PIL import Image

class MarkingReport(pydantic.BaseModel):
    syllabus_code: str = pydantic.Field(..., description="the 4-digit syllabus code shown at the top-right corner of the cover of the mark scheme, e.g. 9701/12 at the top-right of the cover => the syllabus code is 9701")
    component_number: str = pydantic.Field(..., description="the 2-digit component number shown at the top-right corner of the cover of the mark scheme, e.g. 9701/12 at the top-right of the cover => the component number is 12"
    questions: list[Question] = pydantic.Field(..., description="the list of the marked questions")
    strengths: str = pydantic.Field(..., description="areas where the candiate performs well")
    weaknesses: str = pydantic.Field(..., description="areas where the candidate underperformes")

class Question(pydantic.BaseModel):
    question_number: str = pydantic.Field(..., description="the question number, e.g. 3(a)(i), 3(a)(ii), 3(b), 4(a), 5, 6")
    max_marks: int = pydantic.Field(..., description="the maximum marks designed for this question.")
    awarded_marks: int = pydantic.Field(..., description="the marks the student earned.")

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
    ModuleLLMQuery.LLMQuery(
        [
            {"role": "system", "content": "You are a highly experienced senior A-Level examiner who is marking the answers of a candidate. A detailed mark scheme is provided with instructions you will follow consistently and perfectly when grading the candidate's work. The user will provide their completed question paper."},
            {"role": "user", "content": [
                {
                    "type": "text",
                    "text": "These are pages of my question paper."
                },
                {
                    "type"
            ]}
        ],
        response_format=MarkingReport
    )


system_message = {"role": "system", "content": "You are a highly experienced senior A-Level examiner who is marking the answers of a candidate. A detailed mark scheme is provided with instructions you will follow consistently and perfectly when grading the candidate's work."}

def concat_b64imgs(b64_imgs):
    """
    Args:
        b64_imgs: List of base 64 image strings
    Return:
        base 64 string of VERTICALLY concatenated image
    """
    pil_imgs = []
    for b64_img in b64_imgs:
        b64_img = b64_img.split(',')[-1] # Remove data URL prefix
        img_data = base64.b64decode(b64_img)
        img = Image.open(io.BytesIO(img_data))
        pil_imgs.append(img)
    total_height = sum(pil_img.height for pil_img in pil_imgs)
    max_width = max(pil_img.width for pil_img in pil_imgs)
    
    concatenated = Image.new('RGB', (max_width, total_height))
    y_offset = 0
    for pil_img in pil_imgs:
        x_offset = (max_width - pil_img.width) // 2
        concatenated.paste(img, (x_offset, y_offset))
        y_offset += pil_img.height
    
    buffered = io.BytesIO()
    concatenated.save(buffered, format=img_extension_cap)
    return base64.b64encode(buffered.getvalue()).decode()

if __name__ == "__main__":
