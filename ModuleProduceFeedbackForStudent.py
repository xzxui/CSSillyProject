import configs
import pydantic

class Feedback(pydantic.BaseModel):
    Strengths: str = pydantic.Field(..., description="Areas in which the student is performing well")
    Weaknesses: str = pydantic.Field(..., description="Areas where the student is showcasing less proficiency")

def ProduceFeedbackForStudent():
    f
