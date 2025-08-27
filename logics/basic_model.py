import io
import openai
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END     # 그래프 및 종료 지점
from langgraph.graph.message import add_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import ChatMessage #, BaseMessage, SystemMessage, HumanMessage, AIMessage
# from langchain_core.output_parsers import StrOutputParser

load_dotenv()

client = openai.OpenAI()
llm = ChatOpenAI(
    model_name='gpt-4o-mini-2024-07-18', 
    temperature=0.5, 
    streaming=True,
)


basic_styles = '스타일은 10가지로 문어체, 구어체, 감성체, 마케팅체, 뉴스체, 논문체, SNS체, 시적체, 어린이체, 사극체 입니다.'

system_prompt = """당신은 한국어 전문가 입니다. 
한글로 입력된 문장을 다음과 같은 스타일에 맞게 자연스러운 문장으로 변환하여 표현해 주세요."""

check_sentence_prompt = """
다음 문장이 불완전하거나 의미없는 무작위 키 입력(예: 'ㅁㄴㅇㄹㅇㅁㄴㅇㄹ')이라면 'no'를 출력하세요.
그 문장이 한글 문법, 맞춤법, 띄어쓰기로 교정 가능하면 'yes'를 출력하세요.

문장: {sentence}
"""

retify_prompt = """
다음 문장에서 한글 문법, 맞춤법, 띄어쓰기를 교정해 주세요. 의미 또는 표현 변경 없이 오직 문법만 수정해 주세요.

문장: {sentence}
"""
generate_prompt = """
다음 입력값에 따라 문장을 생성하세요. 

[원문] {sentence}
[스타일] {styles}
[문장개수] {number}

[출력형식]
- 원문을 바탕으로 스타일에 맞게 문장을 생성하세요.
- 각 스타일마다 {number}개의 문장만 생성하세요.
- 각 문장은 코드블록으로 감싸 클립보드 복사가 가능해야 합니다.
- 출력 예시는 아래와 같습니다.

예시 입력: 
[원문] 오늘은 날씨가 참 좋다 
[스타일] 스타일은 SNS체 입니다 
[문장개수] 2 

예시 출력:
**원문:**
```
오늘은 날씨가 참 좋다.  
```
**SNS체:**
```
날씨 미쳤다 ☀️ #맑음 #행복    
```
```
화창한 한늘과 새하얀 뭉게구름이 외출을 부르는구나 💨 #야외      
```

"""

def speech_to_text(voice):
    with io.BytesIO(voice.getvalue()) as file:
        file.name = 'voice.wav'
        transcription = client.audio.transcriptions.create(		# 음성 인식
            model='whisper-1',		# 음성 인식 모델
            file=file,
            language='ko'
        )
    return transcription.text		# 음성 인식 결과 텍스트


# 상태 모델(State) 정의
class QAState(TypedDict):
    styles: Annotated[str, 'Style question']
    number: Annotated[int, 'Number of output sentences per style']
    sentence: Annotated[str, 'User input sentence']
    generation: Annotated[str, 'LLM generated answer']
    messages: Annotated[list[ChatMessage], add_messages]

# 조건 모델 정의
class Condition(BaseModel):
    check: str = Field(description="Indicate 'yes' or 'no' whether it is OK")

    
# def init_state(state: QAState) -> QAState:
#     state['messages'] = [ChatMessage(role='system', content=system_prompt)]
#     state['styles'] = basic_styles
#     state['number'] = 1
#     return state

# 노드(Node) 정의
def init(state: QAState) -> QAState:
    if not state['messages']:
        state['messages'] = [ChatMessage(role='system', content=system_prompt)]
    if not state['styles']:
        state['styles'] = basic_styles
        state['number'] = 1
    return state

def set_generation(state: QAState) -> QAState:
    add_kwargs = {'sentence': state['sentence']}        # 원본 입력 문장
    content = "입력하신 문장이 이해하기 어렵습니다. 다시 정확히 입력해 주세요."
    messages = state['messages']
    messages.append(ChatMessage(role='user', content=content, additional_kwargs=add_kwargs))
    messages.append(ChatMessage(role='assistant', content=content))
    return QAState(messages=messages, generation=content)
    
def rectify(state: QAState) -> QAState:
    prompt = retify_prompt.format(**state)
    response = llm.invoke([system_prompt, prompt])
    return QAState(messages=state['messages'], generation=response.content, sentence=state['sentence'])

def generate(state: QAState) -> QAState:
    add_kwargs = {'sentence': state['sentence']}        # 원본 입력 문장
    state['sentence'] = state['generation']     # 수정된 입력 문장을 원본 입력 문장에 설정
    prompt = generate_prompt.format(**state)
    messages = state['messages']
    messages.append(ChatMessage(role='user', content=prompt, additional_kwargs=add_kwargs))
    # chain = ChatPromptTemplate.from_messages(messages) | llm | StrOutputParser()
    # response = chain.invoke({})
    response = llm.invoke(messages)
    messages.append(ChatMessage(role='assistant', content=response.content))
    return QAState(messages=messages, generation=response.content)

def check_Sentence(state: QAState):
    structured_llm = llm.with_structured_output(Condition)
    temp_prompt = ChatPromptTemplate.from_messages([
        ('system', system_prompt),
        ('user', check_sentence_prompt)
    ])
    checker = temp_prompt | structured_llm
    response = checker.invoke(state)
    print(response.check)
    if response.check == 'yes':
        return 'rectify'
    else:
        return 'set_generation'



# 모델 구축
def compiled_graph():
    # 상태(State) 정의
    graph = StateGraph(QAState)
    # 노드(Node) 정의
    graph.add_node('init', init)
    graph.add_node('set_generation', set_generation)
    graph.add_node('rectify', rectify)
    graph.add_node('generate', generate)
    # 흐름(Edge) 연결
    graph.set_entry_point('init')
    # graph.add_edge('init', 'rectify')
    graph.add_conditional_edges('init', check_Sentence)
    graph.add_edge('rectify', 'generate')
    graph.add_edge('set_generation', END)
    graph.add_edge('generate', END)
    # 그래프 빌드(컴파일)
    return graph.compile()

# 실행
def invoke(state, style=None):
    app = compiled_graph()
    result = app.invoke(state)
    return result



if __name__ == "__main__":
    state = {'sentence': 'asdf한s글d'}
    result = invoke(state)
    print(result['generation'])
    
    state.update(result)
    state.update({'sentence': '잠을 못잤더니 머리가 터지겠네'})
    result = invoke(state)
    print(result['generation'])
        
    state.update(result)
    state.update({'sentence': '하마동가랑뉘'})
    result = invoke(state)
    print(result['generation'])
        
    state.update(result)
    state.update({'sentence': '되는일이하나두엄네'})
    result = invoke(state)
    for i, x in enumerate(result['messages']):
        print(i, x.role, x.additional_kwargs.get('sentence'), x.content[:10], '...')
