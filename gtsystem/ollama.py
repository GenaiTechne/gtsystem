import ollama
import base64
import requests

from .instrument import instrument

@instrument.track
def llama_text(system='', prompt='', temperature=0.0, topP=1.0, model='llama2'):
    response = ollama.generate(model=model, prompt=prompt, system=system, 
                               options={
                                   "temperature": temperature,
                                   "top_p": topP
                               })
    return response['response']

@instrument.track
def mistral_text(system='', prompt='', temperature=0.0, topP=1.0, model='mistral'):
    response = ollama.generate(model=model, prompt=prompt, system=system, 
                               options={
                                   "temperature": temperature,
                                   "top_p": topP
                               })
    return response['response']

@instrument.track
def codellama(system='', prompt='', temperature=0.0, topP=1.0, model='codellama'):
    response = ollama.generate(model=model, prompt=prompt, system=system, 
                               options={
                                   "temperature": temperature,
                                   "top_p": topP
                               })
    return response['response']

def get_as_base64(url):
    return base64.b64encode(requests.get(url).content).decode("utf-8")

@instrument.track
def llava_url(system='', prompt='', url='', temperature=0.0, topP=1.0, model='llava'):
    images = [get_as_base64(url)]
    response = ollama.generate(model=model, prompt=prompt, system=system, images=images,
                               options={
                                   "temperature": temperature,
                                   "top_p": topP
                               })
    return response['response']

