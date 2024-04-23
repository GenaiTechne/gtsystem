from openai import OpenAI
from .chat import GptChat
from .instrument import metrics
from IPython.display import clear_output

OPENAI = None

def init():
    global OPENAI
    OPENAI = OpenAI()

CHAT = GptChat()

def _gpt_chat(prompt, system='', temperature=0.0, topP=1, tokens=512, image_url="", 
              reset=False, cache=False, model=""):
    if OPENAI is None:
        init()

    if cache:
        cache_match = CHAT.match(prompt)
        if cache_match:
            CHAT.load(cache_match)
            yield next(msg['content'] for msg in CHAT.messages if msg['role'] == 'assistant')
    else:
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
            stream=True
        )
        all_chunks = ""
        for chunk in response:
            part = chunk.choices[0].delta.content
            if part:
                yield part
                all_chunks += part
        response_text = all_chunks
        CHAT.add_message("assistant", response_text)

@metrics.track
def gpt4_chat(prompt, system='', temperature=0.0, topP=1, tokens=512, image_url="", reset=False, cache=False):
    for chunk in _gpt_chat(prompt, system=system, temperature=temperature, topP=topP, tokens=tokens, 
                           image_url=image_url, reset=reset, cache=cache, model="gpt-4-turbo"):
        yield chunk

@metrics.track
def gpt3_chat(prompt, system='', temperature=0.0, topP=1, tokens=512, reset=False, cache=False):
    for chunk in _gpt_chat(prompt, system=system, temperature=temperature, topP=topP, tokens=tokens, 
                           reset=reset, cache=cache, model="gpt-3.5-turbo"):
        yield chunk

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
        stream=True
    )
    for chunk in response:
        part = chunk.choices[0].delta.content
        if part:
            yield part

@metrics.track
def gpt3_text(prompt, system='', temperature=0.0, topP=1, tokens=512):
    for chunk in _gpt_text(prompt, system=system, temperature=temperature, topP=topP, 
                           tokens=tokens, model="gpt-3.5-turbo"):
        yield chunk

@metrics.track
def gpt4_text(prompt, system='', temperature=0.0, topP=1, tokens=512):
    for chunk in _gpt_text(prompt, system=system, temperature=temperature, topP=topP, 
                     tokens=tokens, model="gpt-4-turbo-preview"):
        yield chunk

def text(prompt, system='', temperature=0.0, topP=1, tokens=512, model="gpt4"):
    match model:
        case 'gpt4':
            for chunk in gpt4_text(prompt, system, temperature, topP, tokens):
                yield chunk
        case 'gpt3.5':
            for chunk in gpt3_text(prompt, system, temperature, topP, tokens):
                yield chunk
        case _:
            return 'Please specify a valid model name'

def chat(prompt, system='', temperature=0.0, topP=1, tokens=512, reset=False, stream=False, cache=False,
         image_url="", model="gpt4"):
    match model:
        case 'gpt4':
            for chunk in gpt4_chat(prompt, system=system, temperature=temperature, topP=topP, 
                                   tokens=tokens, reset=reset, cache=cache, image_url=image_url):
                yield chunk
        case 'gpt3.5':
            for chunk in gpt3_chat(prompt, system=system, temperature=temperature, topP=topP, 
                                   tokens=tokens, reset=reset, cache=cache):
                yield chunk
        case _:
            return 'Please specify a valid model name'
