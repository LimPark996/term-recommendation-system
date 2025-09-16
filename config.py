import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv() 

# ===== 환경변수에서 민감한 정보 로드 =====
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# 개발/테스트용 기본값 (실제 운영에서는 사용하지 말 것)
if not SPREADSHEET_ID:
    print("⚠️ SPREADSHEET_ID 환경변수가 설정되지 않았습니다.")
    
if not OPENAI_API_KEY:
    print("⚠️ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")

# ===== 컬럼 매핑 =====
COLUMN_MAPPING = {
    'term_abbr': '공통표준용어영문약어명',
    'term_name': '공통표준용어명', 
    'term_desc': '공통표준용어설명',
    'domain': '공통표준도메인명',
    'word_name': '공통표준단어명',
    'word_abbr': '공통표준단어영문약어명'
}

# ===== OpenAI 설정 =====
OPENAI_CONFIG_IMP = {
    'model': 'gpt-4o-mini',
    'max_tokens': 250,
    'temperature': 0.3
}

OPENAI_CONFIG_REC = {
    'model': 'gpt-3.5-turbo',
    'max_tokens': 20,
    'temperature': 0.2
}

# ===== 파일 경로 =====
# 기본 경로 (환경변수로 오버라이드 가능)
DEFAULT_FILE_PATH = 'embeddingData_v1(0829).xlsx'
FILE_PATH = os.getenv('EXCEL_FILE_PATH', DEFAULT_FILE_PATH)