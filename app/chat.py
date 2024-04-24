# Remove these two lines when gtsystem is installed
import sys
sys.path.append('../gtsystem')

import streamlit as st
from gtsystem import openai, ollama, anthropic

if "model" not in st.session_state:
    st.session_state["model"] = "OpenAI GPT 3.5 Turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_message" not in st.session_state:
    st.session_state["system_message"] = ""

if "temperature" not in st.session_state:
    st.session_state["temperature"] = 0.3

if "max_tokens" not in st.session_state:
    st.session_state["max_tokens"] = 100

st.title(f"Chat with {st.session_state.model.upper()}")

with st.sidebar:
    st.selectbox("Model", 
                 options=["OpenAI GPT 3.5 Turbo", "OpenAI GPT 4 Turbo",
                          "Phi3 3.8B on Ollama", "Llama3 8B on Ollama", "Mistral 7B on Ollama",
                          "Gemma 9B on Ollama", 
                          "Opus on Anthropic", "Sonnet on Anthropic", "Haiku on Anthropic"], 
                 key="model")
    st.text_area("System message", key="system_message")
    st.slider("Temperature", min_value=0.0, max_value=1.0, step=0.1, key="temperature")
    st.slider("Max tokens", min_value=1, max_value=2048, step=1, key="max_tokens")
    st.button("Clear chat", on_click=lambda: st.session_state.clear())

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if "OpenAI" in st.session_state.model:
            model_name = st.session_state.model.replace("OpenAI ", "").replace(" ", "-").lower()
            stream = openai.chat(prompt=prompt, 
                            model=model_name, 
                            system=st.session_state.system_message,
                            temperature=st.session_state.temperature,
                            tokens=st.session_state.max_tokens)
            response = st.write_stream(stream)
        
        if "Anthropic" in st.session_state.model:
            model_name = st.session_state.model.replace(" on Anthropic", "").lower()
            stream = anthropic.chat(prompt=prompt, 
                            model=anthropic.MODELS[model_name], 
                            system=st.session_state.system_message,
                            temperature=st.session_state.temperature)
            response = st.write_stream(stream)
        
        if "Ollama" in st.session_state.model:
            model_name = st.session_state.model.replace(" on Ollama", "").split(" ")[0].lower()
            stream = ollama.chat(prompt=prompt, 
                            model=model_name, 
                            system=st.session_state.system_message,
                            temperature=st.session_state.temperature)
            response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})