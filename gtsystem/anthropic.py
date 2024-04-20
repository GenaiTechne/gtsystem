import anthropic
from .instrument import metrics
from .chat import ClaudeChat

def _claude3_text(prompt, system='', temperature=0.0, topP=1, tokens=512, model=""):
    message  = anthropic.Anthropic().messages.create(
        model=model,
        system=system,
        temperature=temperature,
        top_p=topP,
        max_tokens=tokens,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text

CHAT = ClaudeChat()

def _claude3_chat(prompt, system='', temperature=0.0, topP=1, tokens=4096, model="", image_url="", 
                  reset=False, cache=False):
    if cache:
        cache_match = CHAT.match(prompt)
        if cache_match:
            CHAT.load(cache_match)
            return next(msg['content'] for msg in CHAT.messages if msg['role'] == 'assistant')

    if reset:
        CHAT.reset_context()
    
    if system != "":
        CHAT.set_system(system)
    
    if image_url != "":
        CHAT.add_image_message(prompt=prompt, image_url=image_url)
    else:
        CHAT.add_message("user", prompt)

    message  = anthropic.Anthropic().messages.create(
        model=model,
        system=CHAT.get_system(),
        temperature=temperature,
        top_p=topP,
        max_tokens=tokens,
        messages=CHAT.get_messages()
    )
    CHAT.add_message("assistant", message.content[0].text)
    return message.content[0].text

@metrics.track
def sonnet_chat(prompt, system='', temperature=0.0, topP=1.0, tokens=512, image_url="", 
                reset=False, cache=False):
    return _claude3_chat(prompt, system=system, 
                         temperature=temperature, topP=topP, tokens=tokens, 
                         model='claude-3-sonnet-20240229',
                         image_url=image_url, reset=reset, cache=cache)

@metrics.track
def opus_chat(prompt, system='', temperature=0.0, topP=1.0, tokens=512, image_url="", 
              reset=False, cache=False):
    return _claude3_chat(prompt, system=system, 
                         temperature=temperature, topP=topP, tokens=tokens, 
                         model='claude-3-opus-20240229',
                         image_url=image_url, reset=reset, cache=cache)

@metrics.track
def haiku_chat(prompt, system='', temperature=0.0, topP=1.0, tokens=512, image_url="", 
               reset=False, cache=False):
    return _claude3_chat(prompt, system=system, 
                         temperature=temperature, topP=topP, tokens=tokens, 
                         model='claude-3-haiku-20240307',
                         image_url=image_url, reset=reset, cache=cache)

@metrics.track
def opus_text(prompt, system='', temperature=0.0, topP=1.0, tokens=512):
    return _claude3_text(prompt, system=system, 
                         temperature=temperature, topP=topP, tokens=tokens, 
                         model='claude-3-opus-20240229')

@metrics.track
def sonnet_text(prompt, system='', temperature=0.0, topP=1.0, tokens=512):
    return _claude3_text(prompt, system=system, 
                         temperature=temperature, topP=topP, tokens=tokens, 
                         model='claude-3-sonnet-20240229')

@metrics.track
def haiku_text(prompt, system='', temperature=0.0, topP=1.0, tokens=512):
    return _claude3_text(prompt, system=system, 
                         temperature=temperature, topP=topP, tokens=tokens, 
                         model='claude-3-haiku-20240307')

def text(prompt, system='', temperature=0.0, topP=1.0, tokens=512, model='opus'):
    match model:
        case 'opus':
            return opus_text(prompt, system, temperature, topP, tokens)
        case 'sonnet':
            return sonnet_text(prompt, system, temperature, topP, tokens)
        case 'haiku':
            return haiku_text(prompt, system, temperature, topP, tokens)
        case _:
            return 'Please specify a valid model name'
