import streamlit as st
from openai import OpenAI
import tiktoken

st.title("Lab 3")

system_prompt = {'role': 'system', 'content': ("You are a helpful assistant."
    "Your job is to get a user's question, answer it, then ask if the user wants more info afterwards."
    "If the user says yes, provide more information and then ask again if they want more info."
    "If the user says no, go back to asking what you can help with."
    "Make sure you give your answers in a manner that a 10 year old can understand.")}

model = st.sidebar.selectbox('Which model?', ('mini', 'nano'))
max_tokens = st.sidebar.slider('max_tokens (token buffer)', 500, 4000, 2000, 100)

if model == "mini":
    model_to_use = "gpt-5-mini"
if model == "nano":
    model_to_use = "gpt-5-nano"

if 'client' not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.client = OpenAI(api_key=api_key)

if 'messages' not in st.session_state:
    st.session_state['messages'] = \
        [{'role': 'assistant', 'content': 'How can I help you?'}]

for msg in st.session_state.messages:
    chat_msg = st.chat_message(msg['role'])
    chat_msg.write(msg['content'])

if prompt := st.chat_input("What's up?"):
    st.session_state.messages.append({'role': 'user', 'content': prompt})

    with st.chat_message('user'):
        st.markdown(prompt)

    recent_messages = st.session_state.messages[-4:]

    max_tokens = 500
    encoding = tiktoken.get_encoding("cl100k_base")
    recent_messages = []
    current_tokens = 0
    
    for msg in reversed(st.session_state.messages):
        msg_tokens = len(encoding.encode(msg['content']))
        if current_tokens + msg_tokens > max_tokens:
            break
        recent_messages.insert(0, msg)
        current_tokens += msg_tokens

    client = st.session_state.client
    stream = client.chat.completions.create(
        model=model_to_use,
        messages=st.session_state.messages,
        stream=True
    )

    with st.chat_message('assistant'):
        response = st.write_stream(stream)

    st.session_state.messages.append({'role': 'assistant', 'content': response})

    completion = client.chat.completions.create(
        model=model_to_use,
        messages = [
            {'role': 'system', 'content': ("You are a helpful assistant."
            "Your job is to get a user's question, answer it, then ask if the user wants more info afterwards."
            "If the user says yes, provide more information and then ask again if they want more info."
            "If the user says no, go back to asking what you can help with."
            "Make sure you give your answers in a manner that a 10 year old can understand.")},
            {'role': 'user', 'content': 'message 1 content.'},
            {'role': 'assistant', 'content': 'message 2 content.'},
            {'role': 'user', 'content': 'message 3 content.'},
            {'role': 'assistant', 'content': 'message 4 content.'}
        ]
    )

