import os
from groq import Groq
from .instrument import metrics
GROQ = None

GROQ = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def _groq_text(prompt, system='', temperature=0.0, topP=1, tokens=512, model=""):
    chat_completion = GROQ.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system,
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model,
        temperature=temperature,
        top_p=topP,
        max_tokens=tokens
    )

    return chat_completion.choices[0].message.content

@metrics.track
def mixtral_text(prompt, system='', temperature=0.0, topP=1, tokens=512, model="mixtral-8x7b-32768"):
    return _groq_text(prompt, system='', temperature=0.0, topP=1, tokens=512, model=model)

@metrics.track
def llama3_text(prompt, system='', temperature=0.0, topP=1, tokens=512, model="llama3-70b-8192"):
    return _groq_text(prompt, system='', temperature=0.0, topP=1, tokens=512, model=model)

@metrics.track
def llama2_text(prompt, system='', temperature=0.0, topP=1, tokens=512, model="llama2-70b-4096"):
    return _groq_text(prompt, system='', temperature=0.0, topP=1, tokens=512, model=model)


def text(prompt, system='', temperature=0.0, topP=1, tokens=512, model="llama3"):
    match model:
        case 'mixtral':
            return mixtral_text(prompt, system=system, temperature=temperature, topP=topP, 
                              tokens=tokens)
        case 'llama3':
            return llama3_text(prompt, system=system, temperature=temperature, topP=topP, 
                              tokens=tokens)
        case 'llama2':
            return llama2_text(prompt, system=system, temperature=temperature, topP=topP, 
                              tokens=tokens)
        case _:
            return 'Please specify a valid model name'
