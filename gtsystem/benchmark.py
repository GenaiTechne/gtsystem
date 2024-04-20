from .anthropic import opus_text
import yaml

def config_quality_criteria():
    # Example usage with data from a file
    file_path = '../data/config.yaml'

    # Read the data from the file
    with open(file_path, 'r') as file:
        data = file.read()    

    # Parse the YAML formatted string
    criteria_data = yaml.safe_load(data)
    
    # Initialize a list to store the formatted criteria strings
    formatted_criteria = []
    
    # Iterate over each criteria in the 'quality' key
    for item in criteria_data['quality']:
        # Extract the criteria description and weight
        criteria = item.get('criteria', 'Undefined criteria')
        weight = item.get('weight', 0)
        
        # Format the string as required and add to the list
        formatted_criteria.append(f'- {criteria} | weight: {weight}')
    
    # Join all formatted strings with a newline
    return '\n'.join(formatted_criteria)

def quality(prompt, system='', result=''):
    system = f"""You are an expert evaluator of an LLM response 
    who can reflect on an LLM response, to a given system and/or user prompt,
    and assess a quality score on a scale of 0 for low to 100 for high quality.
    Think step by step to assess quality based on criteria and associated weights:
    {config_quality_criteria()}
    Respond with a markdown table with columns for Criteria, Weight, Score, Explaination (one sentence).
    Tally the weighted scores in your mind and respond in following format:
    Overall quality score = 98.3/100."""
    prompt = f"""Assess the quality of the following LLM response based on the 
    given System and/or User prompt:
    System: {system} 
    User: {prompt}
    Response: {result}"""
    
    quality_score = opus_text(prompt=prompt, system=system)
    return quality_score
