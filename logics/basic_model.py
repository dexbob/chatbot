import io
import yaml
import openai
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import ChatMessage #, BaseMessage, SystemMessage, HumanMessage, AIMessage
# from langchain_core.output_parsers import StrOutputParser

# 환경설정파일 로드
load_dotenv()

# openai 클라이언트 정의 (STT에 사용)
client = openai.OpenAI()

# langchain의 LLM 객체 정의
llm = ChatOpenAI(
    model_name='gpt-4o-mini-2024-07-18', 
    temperature=0.5, 
    streaming=True,
)

# 프롬프트 정보 추출
with open('logics/prompts.yaml', encoding='utf-8') as f:
    data = yaml.safe_load(f)
    
basic_styles = data['basic_styles']
system_prompt = data['system_prompt']
check_sentence_prompt = data['check_sentence_prompt']
retify_prompt = data['retify_prompt']
generate_prompt = data['generate_prompt']


# STT 함수 (음성인식)
def speech_to_text(voice):
    with io.BytesIO(voice.getvalue()) as file:
        file.name = 'voice.wav'     # 파일명을 설정해줘야 파일로 읽음
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
    state = {'sentence': 'asdf한s글d', 'styles':''}
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
