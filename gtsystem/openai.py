
from .instrument import instrument
from .openai_master import gpt_master

@instrument.track
def gpt_text(system='', prompt='', temperature=0.0, topP=1, tokens=512, model="gpt-3.5-turbo"):
    response = gpt_master(system=system, prompt=prompt, temperature=temperature, 
                          topP=topP, tokens=tokens, model=model)
    return response