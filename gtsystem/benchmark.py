from .openai_master import gpt_master

def accuracy(system='', prompt='', result=''):
    openai_system = """You are evaluating the accuracy of an LLM response. You will be given a system prompt and/or a user prompt, and response from an LLM and you will evaluate the response accuracy as a percentage to second decimal relative to your own response to the same system and/or user prompt. If you can evaluate the accuracy, you will  only respond with the response accuracy number. If you are not able to evaluate the accuracy, you will respond with the reason why you cannot evaluate the response."""
    openai_prompt = f"""Evaluate the accuracy of the following LLM response based on the given System and/or User prompt:
    System: {system} 
    User: {prompt}
    Response: {result}"""

    accuracy = gpt_master(system=openai_system, prompt=openai_prompt)
    return accuracy
