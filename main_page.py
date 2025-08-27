import uuid
import streamlit as st
from datetime import datetime
from logics.basic_model import compiled_graph, init_state
from langchain_core.runnables import RunnableConfig

st.set_page_config(
    page_icon="✨",
    page_title="문장 추천 서비스",
    # layout="wide"
)
def save_chat_log(message):
    chat_log = datetime.now().strftime("logs/debug_%y%m%d.log")
    with open(chat_log, 'a', encoding='utf8') as f:
        f.write(message)
                
def stream_data(app, inputs, config):
    for chunk_msg, metadata in app.stream(inputs, config, stream_mode="messages"):
        yield chunk_msg.content 


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
            st.markdown(content)
            
    
    style_input = st.chat_input('스타일을 입력해 주세요. (공백은 기본 스타일로 출력합니다)')    
    user_input = st.chat_input('대상 문장을 입력하세요.')

    if style_input and style_input.strip() != '':
        state.update({'styles':style_input, 'number':5})
        
    if user_input and user_input.strip() != '':
        with st.chat_message('user'):
            st.markdown(user_input)
        
        # config = RunnableConfig(recursion_limit=10, configurable={"thread_id": str(uuid.uuid4())})
        app = compiled_graph()
        
        state.update({'sentence': user_input})

        with st.spinner('thinking...'):
            result = app.invoke(state)
            with st.chat_message('assistant'):
                st.write(result['generation'])
                # stream = stream_data(app, {'sentence': user_input}, config)
                # result = st.write_stream(stream)
                
        st.session_state.state = result

if __name__ == "__main__":
    run()
