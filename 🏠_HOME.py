# import uuid
import streamlit as st
# from datetime import datetime
from logics.basic_model import compiled_graph, speech_to_text
# from langchain_core.runnables import RunnableConfig

st.set_page_config(
    page_icon="✨",
    page_title="문장 추천 서비스",
    # layout="wide"
)

# def save_chat_log(message):
#     chat_log = datetime.now().strftime("logs/debug_%y%m%d.log")
#     with open(chat_log, 'a', encoding='utf8') as f:
#         f.write(message)
                
# def stream_data(app, inputs, config):
#     for chunk_msg, metadata in app.stream(inputs, config, stream_mode="messages"):
#         yield chunk_msg.content 

def clear_style_input():
    st.session_state.style_input = ''

def style_voice_input():
    if voice:= st.session_state.style_voice:
        st.session_state.style_input = speech_to_text(voice)

def chat_voice_input():
    if voice:= st.session_state.chat_voice:
        st.session_state.user_input = speech_to_text(voice)

# @st.dialog('테스트')
def run() -> None:
    st.title('문장 추천 서비스')
    
    if 'state' not in st.session_state:
        st.session_state.state = {'messages': []}

    state = st.session_state.state
    
    # 이전 대화 정보 출력
    for msg in state['messages']:
        if msg.role == 'system':
            continue
        elif msg.role == 'user':
            content = msg.additional_kwargs.get('sentence')
        elif msg.role:
            content = msg.content
        with st.chat_message(msg.role):
            st.write(content)
            
    with st.sidebar:
        st.subheader("[서브메뉴]")
        style_input = st.text_input('스타일 입력창', key='style_input')
        st.button('스타일 제거 (기본 스타일)', width='stretch', on_click=clear_style_input)
        st.audio_input('스타일🎤', key='style_voice', on_change=style_voice_input)
        st.audio_input('텍스트🎤', key='chat_voice', on_change=chat_voice_input)

    user_input = st.chat_input('대상 문장을 입력하세요.', key='user_input')
    
    if user_input and user_input.strip() != '':
        with st.chat_message('user'):
            st.write(user_input)

        # config = RunnableConfig(recursion_limit=10, configurable={"thread_id": str(uuid.uuid4())})
        app = compiled_graph()

        state.update({'styles':style_input.strip(), 'number':10})
        state.update({'sentence': user_input})

        with st.spinner('thinking...'):
            result = app.invoke(state)
            with st.chat_message('assistant'):
                st.write(result['generation'])
                # stream = stream_data(app, {'sentence': user_input}, config)
                # result = st.write_stream(stream)
                
        st.session_state.state = result
        st.rerun()
    
    
if __name__ == "__main__":
    run()
