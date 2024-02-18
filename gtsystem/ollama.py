import ollama

from .instrument import metrics

@metrics.track
def llama_text(system='', prompt='', temperature=0.0, topP=1.0, model='llama2'):
    response = ollama.generate(model=model, prompt=prompt, system=system, 
                               options={
                                   "temperature": temperature,
                                   "top_p": topP
                               })
    return response['response']

@metrics.track
def mistral_text(system='', prompt='', temperature=0.0, topP=1.0, model='mistral'):
    response = ollama.generate(model=model, prompt=prompt, system=system, 
                               options={
                                   "temperature": temperature,
                                   "top_p": topP
                               })
    return response['response']

@metrics.track
def codellama(system='', prompt='', temperature=0.0, topP=1.0, model='codellama'):
    response = ollama.generate(model=model, prompt=prompt, system=system, 
                               options={
                                   "temperature": temperature,
                                   "top_p": topP
                               })
    return response['response']


