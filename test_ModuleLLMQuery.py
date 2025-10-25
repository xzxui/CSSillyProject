import pydantic
import ModuleLLMQuery

class Person(pydantic.BaseModel):
    name: str
    age: int
    job_type: str = pydantic.Field(..., description="always write 'permanent' for job type")

parsed = ModuleLLMQuery.LLMQuery(
    [
        {
            "role": "system",
            "content": "Fill in the information of this person provided by the user.",
        },
        {
            "role": "user",
            "content": "John is 35 years old and from Europe."
        }
    ],
    response_format=Person
)

print(parsed)
