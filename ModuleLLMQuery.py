import configs
import openai

client = openai.OpenAI(
        base_url = configs.base_url,
        api_key = configs.api_key, 
)

def LLMQuery(messages, response_format=None, model=configs.llm_model):
    """
    Args:
        1. messages (<class 'list'>): Message history feeded to the LLM, refer to platform.openai.com for details
        2. response_format (None / Pydantic.BaseModel): Set this to None if you are not using structured output, otherwise set this to the pydantic BaseModel class you're using
        3. model (<class 'str'>): LLM model used
    Return:
        If you are NOT using strucutred output:
            Return the text response of the AI
        If you are using strucutred output:
            Return the returned pydantic BaseModel instance from the AI
    """
    if response_format == None:
        completion = client.chat.completions.parse(
            model = model,
            messages = messages,
        )
    else:
        completion = client.chat.completions.parse(
            model = model,
            messages = messages,
            response_format = response_format,
        )
    message = completion.choices[0].message
    if message.refusal:
        print(message)
        raise RuntimeError("Shit! Our llm request refused!")
    if response_format == None:
        return message.content
    else:
        return message.parsed

# For Testing
# The testing prompt is from platform.openai.com
"""
result = query(
    [
        {"role": "system", "content": "You are a helpful math tutor. Guide the user through the solution step by step."},
        {"role": "user", "content": "how can I solve 8x + 7 = -23"},
    ],
)
print(result)
"""
