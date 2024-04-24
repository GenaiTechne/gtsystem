import ollama
from .chat import OllamaChat

MODELS = {
    'llama3': 'llama3',
    'mistral': 'mistral',
    'gemma': 'gemma',
    'phi3': 'phi3',
}

def text(prompt, system='', temperature=0.0, topP=1.0, model='llama3'):
    response = ollama.generate(model=model, prompt=prompt, system=system, stream=True,
                               options={
                                   "temperature": temperature,
                                   "top_p": topP
                               })
    for chunk in response:
        if chunk:
            yield chunk['response']

CHAT = OllamaChat()

def chat(prompt, system='', temperature=0.0, topP=1, reset=False, cache=False, model="llama3"):
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

        CHAT.add_message("user", prompt)
        
        response = ollama.chat(
            model=model,
            messages=CHAT.get_messages(),
            stream=True,
            options={"temperature": temperature, "top_p": topP}
        )
        response_text = ""
        for chunk in response:
            part = chunk['message']['content']
            if part:
                yield part
                response_text += part
        CHAT.add_message("assistant", response_text)
