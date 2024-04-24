from openai import OpenAI
from .chat import GptChat

OPENAI = None

def init():
    global OPENAI
    OPENAI = OpenAI()

CHAT = GptChat()

MODELS = {
    'gpt4': 'gpt-4-turbo',
    'gpt3.5': 'gpt-3.5-turbo'
}

def list_models():
    return ['gpt-4-turbo', 'gpt-3.5-turbo']

def chat(prompt, system='', temperature=0.0, topP=1, tokens=512, image_url="", 
              reset=False, cache=False, model=MODELS['gpt4']):
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

def text(prompt, system='', temperature=0.0, topP=1, tokens=512, model=MODELS['gpt4']):
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
