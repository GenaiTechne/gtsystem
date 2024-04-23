# Remove these two lines when gtsystem is installed
import sys
sys.path.append('../gtsystem')

import streamlit as st
from gtsystem import openai

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt3.5"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_message" not in st.session_state:
    st.session_state["system_message"] = ""

if "temperature" not in st.session_state:
    st.session_state["temperature"] = 0.3

if "max_tokens" not in st.session_state:
    st.session_state["max_tokens"] = 100

st.title(f"Chat with {st.session_state.openai_model.upper()}")

with st.sidebar:
    st.selectbox("Model", options=["gpt3.5", "gpt4"], key="openai_model")
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
        stream = openai.chat(prompt=prompt, 
                             model=st.session_state.openai_model, 
                             system=st.session_state.system_message,
                             temperature=st.session_state.temperature)
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})