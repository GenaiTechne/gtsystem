
from .instrument import metrics
from .openai_master import gpt_master

@metrics.track
def text(prompt, system='', temperature=0.0, topP=1, tokens=512, model="gpt-3.5-turbo"):
    response = gpt_master(prompt=prompt, system=system, temperature=temperature, 
                          topP=topP, tokens=tokens, model=model)
    return response

