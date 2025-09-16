# 🏢 Term Recommendation System

개발자들이 DB를 구성할 때 사용하는 표준 용어와 약어를 관리하고 추천하는 AI 기반 시스템입니다.

## ✨ 주요 기능

### 1. 용어 정의 개선
- 기존 용어의 정의를 AI를 활용하여 더 명확하고 이해하기 쉽게 개선
- 개발자 친화적인 설명으로 자동 변환
- 200-250자 내외의 간결한 정의 제공

### 2. 약어 추천
- 한글 텍스트를 입력하면 적절한 영문 약어 자동 생성
- 기존 표준 용어와의 유사도 분석을 통한 일관성 있는 추천
- KoNLPy를 활용한 형태소 분석으로 정확한 약어 생성

## 🛠️ 기술 스택

- **Python 3.8+**
- **OpenAI GPT API** - 정의 개선 및 약어 생성
- **Google Sheets API** - 용어 데이터 관리
- **KoNLPy** - 한국어 형태소 분석
- **pandas** - 데이터 처리
- **numpy** - 벡터 연산 및 유사도 계산

## 📋 필수 요구사항

### Python 패키지
```bash
pip install -r requirements.txt
```

### API 키 및 인증
1. **OpenAI API 키** - GPT 모델 사용을 위해 필요
2. **Google Sheets API 인증** - OAuth 2.0 또는 서비스 계정

## 🚀 설치 및 설정

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/term-recommendation-system.git
cd term-recommendation-system
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# .env 파일을 열어서 실제 값으로 수정
SPREADSHEET_ID=your_actual_spreadsheet_id
OPENAI_API_KEY=your_actual_openai_api_key
EXCEL_FILE_PATH=data/your_excel_file.xlsx
```

### 5. Google Sheets 인증 설정
처음 실행시 브라우저가 열리며 Google 계정 인증을 진행합니다.

## 🎯 사용법

### 대화형 모드 실행
```bash
python main.py
```

### 메뉴 옵션
1. **용어 정의 개선** - 기존 용어의 정의를 AI로 개선
2. **약어 추천** - 입력한 텍스트에 대한 영문 약어 생성
3. **시스템 종료**

### 사용 예시

#### 용어 정의 개선
```
입력: API_USE_YN
출력: API 사용 여부를 나타내는 플래그. Y(사용), N(미사용)으로 구분되며...
```

#### 약어 추천
```
입력: 계좌번호
출력: ACNT_NO
```

## 📁 프로젝트 구조

```
term-recommendation-system/
├── main.py                 # 메인 실행 파일
├── config.py              # 설정 파일
├── data_loader.py         # 데이터 로드 모듈
├── openai_client.py       # OpenAI API 클라이언트
├── term_processor.py      # 용어 처리 로직
├── requirements.txt       # Python 패키지 목록
├── .env.example          # 환경변수 예시 파일
├── .gitignore           # Git 무시 파일 목록
└── README.md            # 프로젝트 설명서
```

## 🔧 주요 모듈 설명

### main.py - 🎮 시스템 컨트롤러

역할: 사용자와 시스템 간의 인터페이스 담당

주요 기능:

- 인터랙티브 메뉴 제공 (1: 정의개선, 2: 약어추천, 3: 종료)
- 사용자 입력 검증 및 처리
- 각 기능 모듈들을 연결하여 워크플로우 관리
- 에러 처리 및 사용자 피드백

```
코드 흐름:
시작 → 시스템 초기화 → 메뉴 표시 → 사용자 선택 → 해당 기능 실행 → 결과 출력 → 반복
```

### data_loader.py - 📊 데이터 관리자

역할: 외부 데이터 소스와의 연결 및 데이터 로딩 담당

주요 기능:

- Google Sheets OAuth 인증 처리
- 스프레드시트에서 용어/단어 데이터 읽기
- Excel 파일에서 1536차원 임베딩 벡터 로드
- 데이터 정제 및 형식 통일

```
코드 흐름:
OAuth 인증 → Google Sheets 연결 → 시트별 데이터 읽기 → DataFrame 변환 
→ Excel 임베딩 로드 → 데이터 검증 → 다른 모듈에 제공
```

### openai_client.py - 🤖 AI 두뇌

역할: OpenAI GPT와의 통신 및 AI 추론 담당

주요 기능:

- 용어 정의 개선: 기존 설명을 더 명확하고 개발자 친화적으로 변환
- 약어 생성: 한글 단어를 표준 영문 약어로 변환
- 프롬프트 엔지니어링: AI가 정확한 결과를 내도록 명령어 최적화
- API 연결 테스트 및 에러 처리

```
코드 흐름:
입력 텍스트 받기 → 프롬프트 구성 → OpenAI API 호출 
→ 응답 파싱 → 결과 검증 → 정제된 결과 반환
```

### term_processor.py - 🧠 핵심 로직 엔진

역할: 자연어 처리 및 유사도 계산을 통한 스마트 매칭

주요 기능:

- KoNLPy로 한국어 형태소 분석 (조사, 어미 제거)
- OpenAI 임베딩을 사용한 의미적 유사도 계산
- 기존 표준 용어와 신규 요청의 매칭
- 약어 조합 및 최적화

```
코드 흐름:
한글 입력 → 형태소 분석 → 각 단어별 임베딩 생성 → 기존 용어들과 유사도 계산 
→ 임계값(0.3) 이상인 것들 선별 → 매칭되면 기존 약어 사용, 없으면 AI로 새 약어 생성 
→ 기존 표준과 충돌 확인 → 최종 약어 반환
```

### config.py - ⚙️ 시스템 설정 파일

역할: 모든 설정값과 매핑 정보 중앙 관리

주요 설정:

- API 키: OpenAI API 키, Google Sheets ID
- 컬럼 매핑: 실제 컬럼명과 코드에서 사용하는 키 매핑
- AI 모델 설정: 사용할 GPT 모델, 토큰 수, 온도값 등
- 파일 경로: 임베딩 데이터가 들어있는 Excel 파일 위치

```
설정 예시:
pythonOPENAI_CONFIG_IMP = {
    'model': 'gpt-4o-mini',      # 정의 개선용 모델
    'max_tokens': 250,           # 최대 토큰 수
    'temperature': 0.3           # 창의성 수준 (낮을수록 일관성↑)
}
```

## 🔒 보안 고려사항

- API 키와 민감한 정보는 환경변수로 관리
- `.env` 파일은 Git에 커밋되지 않도록 설정
- 데이터 파일은 로컬에서만 관리