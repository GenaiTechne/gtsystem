import anthropic
from .chat import ClaudeChat

MODELS = {
    'opus': 'claude-3-opus-20240229',
    'sonnet': 'claude-3-sonnet-20240229',
    'haiku': 'claude-3-haiku-20240307'
}

def text(prompt, system='', temperature=0.0, topP=1, tokens=512,
          model=MODELS['opus']):
    with anthropic.Anthropic().messages.stream(
        model=model,
        system=system,
        temperature=temperature,
        top_p=topP,
        max_tokens=tokens,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            if text:                
                yield text

CHAT = ClaudeChat()

def chat(prompt, system='', temperature=0.0, topP=1, tokens=512, image_url="", 
         reset=False, cache=False, model=MODELS['opus']):
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

    full_text = ""
    with anthropic.Anthropic().messages.stream(
        model=model,
        system=CHAT.get_system(),
        temperature=temperature,
        top_p=topP,
        max_tokens=tokens,
        messages=CHAT.get_messages()
    ) as stream:
        for text in stream.text_stream:
            if text:                
                yield text
                full_text += text

    CHAT.add_message("assistant", full_text)