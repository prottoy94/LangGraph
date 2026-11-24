import streamlit as st
from langchain_core.messages import HumanMessage
from langGraph_database_backend import chatbot, retrive_all_thread_ids

import uuid

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    st.session_state['message_history'] = []
    st.session_state['thread_id'] = generate_thread_id()
    add_thread(st.session_state['thread_id'])
    
def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)
        
def load_conversation(thread_id):
    CONFIG = {'configurable': {'thread_id': thread_id}}
    # a brand-new thread has no saved state yet, so fall back to an empty list
    return chatbot.get_state(config=CONFIG).values.get('messages', [])

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
    
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()
    
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrive_all_thread_ids()
    
CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

add_thread(st.session_state['thread_id'])
    
st.sidebar.title("Chatbot")
if st.sidebar.button("New Chat"):
    reset_chat()
st.sidebar.header("Chat History")

for thread_id in st.session_state['chat_threads']:
    if st.sidebar.button(f"Thread ID: {thread_id}"):
        st.session_state['thread_id'] = thread_id
        message_history = load_conversation(thread_id)
         
        temp_message_history = []
        
        for message in message_history:
            if isinstance(message, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            temp_message_history.append({'role': role, 'content': message.content})
        
        st.session_state['message_history'] = temp_message_history

# show previous messages
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here') 

if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    with st.chat_message('assistant'):
        # stream the response chunk by chunk; write_stream returns the full text
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            )
        )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
