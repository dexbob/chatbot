# 📝 문장 추천 챗봇 (Sentence Recommendation Chatbot)

이 프로젝트는 Streamlit과 LangGraph를 사용하여 구축된 문장 추천 서비스입니다. 사용자가 입력한 문장과 원하는 스타일을 기반으로 새로운 문장을 생성하고 추천해주는 대화형 챗봇입니다.

## ✨ 주요 기능

- **실시간 문장 추천**: LangGraph 기반의 에이전트가 사용자의 요청을 실시간으로 처리하고 문장을 생성합니다.
- **대화형 인터페이스**: Streamlit을 사용하여 직관적이고 사용하기 쉬운 웹 UI를 제공합니다.
- **커스텀 스타일 적용**: 사용자가 원하는 문장 스타일(예: "친근하게", "전문적으로")을 직접 입력하여 결과에 반영할 수 있습니다.
- **음성 입력 지원**: 텍스트 입력뿐만 아니라 음성을 녹음하여 문장을 입력할 수 있습니다. (Speech-to-Text)

## 🛠️ 기술 스택

- **프레임워크**: Streamlit
- **언어**: Python
- **LLM/Agent**: LangChain, LangGraph, OpenAI
- **패키지 관리**: uv

## 🚀 설치 및 실행 방법

1.  **프로젝트 클론**

    ```bash
    git clone <repository-url>
    cd chatbot
    ```

2.  **가상환경 생성 및 활성화** (uv 이용을 권장)

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    ```

3.  **필요한 패키지 설치** (권장)
    `uv.lock` 파일이 있으므로 `uv`를 사용하여 패키지를 동기화합니다.

    ```bash
    pip install uv
    uv sync
    ```

4.  **.env 파일 생성**
    프로젝트 루트 디렉토리에 `.env` 파일을 생성하고, OpenAI API 키를 추가합니다.

    ```
    OPENAI_API_KEY="sk-..."
    ```

5.  **애플리케이션 실행**
    ```bash
    run     # 방법1. 실행파일(.bat) 이용 (내부에서 방법2를 호출)
    uv run main.py      # 방법2. uv를 이용 (내부에서 방법3을 호출)
    streamlit run 🏠_home.py        # 방법3. streamlit 이용해 직접 실행
    ```

## 📁 파일 구조

```
chatbot/
├── .venv/                  # 가상환경
├── logics/
│   └── basic_model.py      # LangGraph 에이전트 및 핵심 로직
├── pages/
│   └── 1_🧾_챗봇.py      # 일반적인 AI 챗봇
│   └── 2_🧸_이미지봇.py      # 이미지 생성 AI 이미지봇
│   └── 3_💘_서비스1단계.py      # 문장 추천 서비스 1단계 과정
│   └── 4_💕_서비스2단계.py      # 문장 추천 서비스 2단계 과정
├── 🏠_home.py              # Streamlit 메인 애플리케이션 (문장 추천 서비스)
├── .env                    # 환경 변수 파일 (*개별 생성: OpenAI API키)
├── requirements.lock       # uv 패키지 락 파일 (uv.lock)
└── README.md               # 프로젝트 설명 파일
```

## 📖 사용법

1.  애플리케이션을 실행하면 웹 브라우저에 챗봇 인터페이스가 나타납니다.
2.  사이드바의 '스타일 입력창'에 원하는 문체나 스타일을 입력합니다. (예: "초등학생도 이해하기 쉽게", "트위터처럼 짧고 간결하게")
3.  하단의 채팅 입력창에 추천받고 싶은 원본 문장을 입력하고 Enter 키를 누릅니다.
4.  음성 입력을 사용하려면 사이드바의 마이크 아이콘(🎤)을 클릭하여 녹음합니다.
5.  챗봇이 실시간으로 새로운 문장을 생성하여 보여줍니다.
