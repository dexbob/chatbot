from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st

# 기본 설정
load_dotenv()
CHAT_LOG = datetime.now().strftime("logs/system_%y%m%d.log")
# client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
client = OpenAI()

st.set_page_config(
    page_icon="✨",
    page_title="스타일 문장 교정 서비스",
    layout="wide"
)


def save_file(*messages):
    with open(CHAT_LOG, 'a') as f:
        for message in messages:
            f.write(message)
            f.write('\n')

def show_chat_message(message: dict, session=True) -> None:
    if message['role'] == 'system':
        return
    if session:
        st.session_state.messages.append(message)
        
    with st.chat_message(message['role']):
        st.write(message['content'])

def run() -> None:
    st.title('문장 교정 서비스')
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "당신은 도움을 주는 훌륭한 조수이다."},
        ]
    
    # 이전 대화 정보 출력
    for msg in st.session_state.messages:
        show_chat_message(msg, False)
    
    user_input = st.chat_input('질문을 넣어주세요.')
    print(user_input)
    if user_input:
        show_chat_message({'role': 'user', 'content': user_input})
        
        res = client.chat.completions.create(
            model='gpt-4o-mini-2024-07-18',     # 적절한 모델
            # model='gpt-3.5-turbo-0125',     # 단문 위주 모델
            # model='gpt-5-nano',     # 저렴한 모델(속도느림)
            messages=st.session_state.messages
        )
        
        result = res.choices[0].message.content        
        show_chat_message({"role": "assistant", "content": result})



if __name__ == "__main__":
    run()
