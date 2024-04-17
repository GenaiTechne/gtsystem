from openai import OpenAI
from .chat import GptChat
from .instrument import metrics

OPENAI = None

def init():
    global OPENAI
    OPENAI = OpenAI()

CHAT = GptChat()

def _gpt_chat(prompt, system='', temperature=0.0, topP=1, tokens=512, image_url="", model="", reset=False):
    if OPENAI is None:
        init()

    if reset:
        CHAT.reset_context()
    
    if system != "":
        CHAT.add_message("system", system)
    
    if image_url != "":
        CHAT.add_image_message(prompt=prompt, image_url=image_url)
    else:
        CHAT.add_message("user", prompt)

    response = OPENAI.chat.completions.create(
        model=model,
        messages=CHAT.get_messages(),
        temperature=temperature,
        top_p=topP,
        max_tokens=tokens,
    )
    response_text = response.choices[0].message.content.strip()
    CHAT.add_message("assistant", response_text)
    return response_text

@metrics.track
def gpt4_chat(prompt, system='', temperature=0.0, topP=1, tokens=512, image_url="", reset=False):
    return _gpt_chat(prompt, system=system, temperature=temperature, 
                topP=topP, tokens=tokens, model="gpt-4-turbo", image_url=image_url, reset=reset)

@metrics.track
def gpt3_chat(prompt, system='', temperature=0.0, topP=1, tokens=512, reset=False):
    return _gpt_chat(prompt, system=system, temperature=temperature, 
                topP=topP, tokens=tokens, model="gpt-3.5-turbo", reset=reset)

def _gpt_text(prompt, system='', temperature=0.0, topP=1, tokens=512, model=""):
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

@metrics.track
def gpt3_text(prompt, system='', temperature=0.0, topP=1, tokens=512):
    return _gpt_text(prompt, system=system, temperature=temperature, 
                topP=topP, tokens=tokens, model="gpt-3.5-turbo")

@metrics.track
def gpt4_text(prompt, system='', temperature=0.0, topP=1, tokens=512):
    return _gpt_text(prompt, system=system, temperature=temperature, 
                topP=topP, tokens=tokens, model="gpt-4-turbo-preview")

def text(prompt, system='', temperature=0.0, topP=1, tokens=512, model="gpt4"):
    match model:
        case 'gpt3':
            return gpt3_text(prompt, system, temperature, topP, tokens)
        case 'gpt4':
            return gpt4_text(prompt, system, temperature, topP, tokens)
        case _:
            return 'Please specify a valid model name'

