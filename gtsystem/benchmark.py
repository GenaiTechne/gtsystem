from .bedrock import claude3_text

def accuracy(prompt, system='', result=''):
    system = """You are evaluating the accuracy of an LLM response. 
    You will be given a system prompt and/or a user prompt, and response from an LLM and 
    you will evaluate the response accuracy as a percentage to second decimal relative to 
    your own response to the same system and/or user prompt. You will only respond with 
    the response accuracy number. If you are not able to evaluate 
    the accuracy, you will respond with 'Cannot Evaluate Accuracy'."""
    prompt = f"""Evaluate the accuracy of the following LLM response based on the 
    given System and/or User prompt:
    System: {system} 
    User: {prompt}
    Response: {result}"""
    
    accuracy = claude3_text(prompt=prompt, system=system)
    return accuracy
