from openai import OpenAI

from .instrument import metrics
OPENAI = None

def init():
    global OPENAI
    OPENAI = OpenAI()

@metrics.track
def gpt(prompt, system='', temperature=0.0, topP=1, tokens=64, model="gpt-3.5-turbo"):
    if OPENAI is None:
        init()

    response = OPENAI.chat.completions.create(
    model=model,
    messages=[
        {
        "role": "system",
        "content": system
        },
        {
        "role": "user",
        "content": prompt
        }
    ],
    temperature=temperature,
    top_p=topP,
    max_tokens=tokens,
    )
    response_text = response.choices[0].message.content.strip()
    return response_text

def text(prompt, system='', temperature=0.0, topP=1, tokens=512, model="gpt-3.5-turbo"):
    response = gpt(prompt=prompt, system=system, temperature=temperature, 
                          topP=topP, tokens=tokens, model=model)
    return response

