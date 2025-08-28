# import uuid
import streamlit as st
from logics.basic_model import compiled_graph
# from langchain_core.runnables import RunnableConfig

st.set_page_config(
    page_icon="✨",
    page_title="문장 추천 서비스",
    # layout="wide"
)


def run() -> None:
    st.title('문장 추천 서비스')
    
    if 'state' not in st.session_state:
        st.session_state.state = {'messages': [], 'styles':''}

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

    if style_input:
        state.update({'styles':style_input.strip(), 'number':5})
        
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
