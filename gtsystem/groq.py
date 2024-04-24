import os
from groq import Groq
GROQ = None

GROQ = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

MODELS = {
    'llama3': 'llama3-70b-8192',
    'mixtral': 'mixtral-8x7b-32768'
}

def text(prompt, system='', temperature=0.0, topP=1, tokens=512, model=MODELS['llama3']):
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
