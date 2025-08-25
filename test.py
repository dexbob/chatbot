import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
prompt = [
    {"role": "system", "content": "당신은 도움을 주는 훌륭한 조수이다."},       # 대화 메시지 초기화
]

def getAnswer(user_input):
    prompt.append({"role": "user", "content": user_input})        # 사용자 질문
    res = client.chat.completions.create(
        model='gpt-3.5-turbo-0125',     # 단문위주
        # model='gpt-5-nano',     # 저렴한 모델(속도느림)
        messages=prompt
    )
    result = res.choices[0].message.content
    prompt.append({"role": "assistant", "content": result})       # 맥락 이어가기
    return result

def save_file(*messages):
    with open('chat_log.txt', 'a', encoding='utf-8') as f:
        for message in messages:
            f.write(message)
            f.write('\n')

def run():
    while True:
        saveFlag = True
        print('='*40, '\n')
        user_input = input('User (Q to quit, 요약): ').strip()
        if user_input in 'Qq':
            print('Bye')
            break
        elif user_input == '요약':
            user_input = '지금까지의 대화를 요약해줘'
            saveFlag = False

        result = getAnswer(user_input)
        saveFlag and save_file(user_input, result)
        print('-'*30, '\n', result)



if __name__ == "__main__":
    print('test')