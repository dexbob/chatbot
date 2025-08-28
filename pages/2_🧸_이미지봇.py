import os
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# 기본 설정
load_dotenv()
# client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
client = OpenAI()

st.set_page_config(
    page_icon="✨",
    page_title="이미지봇 서비스",
    # layout="wide"
)

def save_chat_log():
    chat_log = datetime.now().strftime("logs/debug_%y%m%d.log")
    with open(chat_log, 'a', encoding='utf8') as f:
        for message in st.session_state.messages[-2:]:
            if message['role'] != 'system':
                f.write(f'[{message['role']}]')
                f.write(message['content'])
                f.write('\n')

def run() -> None:
    st.title('이미지봇 서비스')
    
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "당신은 도움을 주는 훌륭한 조수이다."},
        ]
    
    # 이전 대화 정보 출력
    for msg in st.session_state.messages:
        if msg['role'] == 'user':
            with st.chat_message(msg['role']):
                st.markdown(msg['content'])
        elif msg['role'] == 'assistant':
            with st.chat_message(msg['role']):
                st.image(msg['content'])
        
    user_input = st.chat_input('질문을 입력하세요.')
    if user_input:
        msg = {'role': 'user', 'content': user_input}
        st.session_state.messages.append(msg)
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])
        
        with st.spinner('thinking...'):
            res = client.images.generate(
                model='dall-e-3',
                prompt=user_input,
                size='1024x1024',
                quality='standard',
                n=1,
            )
            
        with st.chat_message('assistant'):
            url = res.data[0].url
            st.image(url)
        st.session_state.messages.append({"role": "assistant", "content": url})
        save_chat_log()

if __name__ == "__main__":
    run()
