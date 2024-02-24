from openai import OpenAI
OPENAI = None

def init():
    global OPENAI
    OPENAI = OpenAI()

def gpt_master(prompt, system='', temperature=0.0, topP=1, tokens=64, model="gpt-3.5-turbo"):
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

