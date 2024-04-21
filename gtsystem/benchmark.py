from .anthropic import opus_text
from .openai import gpt4_text
import yaml

QUALITY_SCORE = []

def evaluator_model():
    file_path = '../data/config.yaml'

    with open(file_path, 'r') as file:
        data = file.read()    

    evaluator = yaml.safe_load(data)
    return evaluator['benchmark'][0]['model']

def config_quality_criteria():
    file_path = '../data/config.yaml'

    with open(file_path, 'r') as file:
        data = file.read()    

    criteria_data = yaml.safe_load(data)
    formatted_criteria = []
    
    for item in criteria_data['quality']:
        criteria = item.get('criteria', 'Undefined criteria')
        weight = item.get('weight', 0)
        formatted_criteria.append(f'- {criteria} | weight: {weight}')
    
    return '\n'.join(formatted_criteria)

import re

def extract_quality_score(input_string):
    pattern = r"Average quality score = (\d+\.\d+)/100\.$"
    match = re.search(pattern, input_string)
    
    if match:
        score = float(match.group(1))
        return score
    else:
        return

def quality(prompt, system='', result='', fn=''):
    system = f"""You are an expert evaluator of an LLM response 
    who can reflect on an LLM response, to a given system and/or user prompt,
    and assess a quality score on a scale of 0 for low to 100 for high quality.
    Think step by step to assess quality based on the criteria:
    {config_quality_criteria()}
    Respond with a markdown table with columns for Criteria, Score, Explaination (one sentence).
    Average the scores in your mind and respond in following format:
    Average quality score = 98.3/100."""
    prompt = f"""Assess the quality of the following LLM response based on the 
    given System and/or User prompt:
    System: {system} 
    User: {prompt}
    Response: {result}"""

    evaluator = evaluator_model()
    if evaluator == "gpt4":
        quality_score = gpt4_text(prompt=prompt, system=system)
    else:
        quality_score = opus_text(prompt=prompt, system=system)

    QUALITY_SCORE.append({"Model": fn, "Score": extract_quality_score(quality_score)})
    return quality_score

def stats():
    markdown_table = "| Model | Quality Score |\n"
    markdown_table += "|-------|--------------|\n"
    for item in QUALITY_SCORE:
        model = item["Model"]
        score = item["Score"]
        markdown_table += f"| {model} | {score} |\n"
    return markdown_table