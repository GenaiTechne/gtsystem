import os
from groq import Groq
from .instrument import metrics
GROQ = None

GROQ = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

@metrics.track
def text(prompt, system='', temperature=0.0, topP=1, tokens=512, model="mixtral-8x7b-32768"):
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
