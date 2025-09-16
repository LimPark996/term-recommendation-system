import logging
from typing import List, Dict, Optional, Tuple
from config import COLUMN_MAPPING, OPENAI_API_KEY
from openai_client import OpenAIClient
from konlpy.tag import Okt
import numpy as np
from data_loader import DataLoader
from openai import OpenAI

logger = logging.getLogger(__name__)

class TermProcessor:
    def __init__(self, openai_client: OpenAIClient, data_loader: DataLoader):
        self.openai_client = openai_client
        self.data_loader = data_loader
        self.client = OpenAI(api_key=OPENAI_API_KEY)

        # 데이터 로드
        terms, words = self.data_loader.load_data()
        self.sheet1_abbr_list, self.term_data, self.abbr_data, self.term_embeddings = self.data_loader.load_data_rec(terms, words)
        
        # KoNLPy 초기화
        self.okt = Okt()

        self.worksheet2 = None

    def improve_term_definition(self, term_abbr: str, terms: List[Dict]) -> Dict:
        """용어 정의 개선"""
        logger.info(f'\n🔍 용어 정의 개선 시작: {term_abbr}')
        
        try:
            # 1단계: 용어 검색
            logger.info('1️⃣ 용어 검색 중...')
            target_term = None
            
            abbr_column = COLUMN_MAPPING['term_abbr']
            target_term = next((term for term in terms if term.get(abbr_column) == term_abbr), None)
            
            if not target_term:
                logger.info('❌ 용어를 찾을 수 없음')
                available_columns = list(terms[0].keys()) if terms else []
                sample_terms = [list(term.values())[0] for term in terms[:10]] if terms else []
                
                return {
                    'success': False,
                    'message': '해당 용어를 찾을 수 없습니다.',
                    'term_abbr': term_abbr,
                    'available_columns': available_columns,
                    'sample_terms': sample_terms
                }
            
            # 2단계: 용어 정보 추출
            logger.info('2️⃣ 용어 정보 추출 중...')
            term_name_column = COLUMN_MAPPING['term_name']
            desc_column = COLUMN_MAPPING['term_desc']
            
            term_name = target_term.get(term_name_column, '')
            current_definition = target_term.get(desc_column, '')
            
            logger.info(f'📝 용어명: {term_name}')
            logger.info(f'📝 현재 정의: {current_definition}')
            
            if not term_name or not current_definition:
                return {
                    'success': False,
                    'message': '용어명 또는 설명이 비어있습니다.'
                }
            
            # 3단계: AI 정의 개선
            logger.info('3️⃣ AI 정의 개선 중...')
            improved_definition = self.openai_client.improve_ai_definition(
                term_abbr, term_name, current_definition
            )
            
            if not improved_definition:
                return {
                    'success': False,
                    'message': 'AI 정의 개선에 실패했습니다.'
                }
            
            return {
                'success': True,
                'current_definition': current_definition,
                'improved_definition': improved_definition,
                'message': '정의가 성공적으로 개선되었습니다.'
            }
            
        except Exception as e:
            logger.error(f'❌ improve_term_definition 오류: {e}')
            return {
                'success': False,
                'message': f'시스템 오류: {str(e)}',
                'error': str(e)
            }
            
    
    def get_embedding(self, text: str, model: str = "text-embedding-3-small") -> np.ndarray:
        """텍스트를 OpenAI embedding으로 변환"""
        response = self.client.embeddings.create(input=[text], model=model, dimensions=1536)
        return np.array(response.data[0].embedding)

    def find_permutation_match(self, abbr: List[str], abbr_list: List[str]) -> Optional[str]:
        """생성된 약어와 sheet1 약어 리스트에서 순서 무시 일치 검사"""
        for candidate in abbr_list:
            if set(candidate.split('_')) == set(abbr):
                return candidate
        return None

    def find_most_similar_term(self, word: str) -> Tuple[List[str], List[str]]:
        word_emb = self.get_embedding(word)
        best_term = []
        best_abbr = []
        
        for term, emb in zip(self.term_data, self.term_embeddings):
            if emb is not None and len(emb) == len(word_emb):  # 차원 체크 추가
                sim = np.dot(word_emb, emb) / (np.linalg.norm(word_emb) * np.linalg.norm(emb))
                if sim > 0.3:
                    best_term.append(term)
                    best_abbr.append(self.abbr_data[self.term_data.index(term)])
        
        return best_term, best_abbr

    def recommend_abbreviation(self, text: str) -> List[str]:
        """KoNLPy로 형태소 분석 + embedding 유사도 비교 + 약어 생성/대체"""
        abbr = []
        pos_result = self.okt.pos(text)
        print("검색어 형태소 분석 결과:", pos_result)
        for word, pos in pos_result:
            if word.upper() in self.term_data:
                abbr.append(self.abbr_data[self.term_data.index(word.upper())])
            elif pos not in ['Josa', 'Eomi', 'Punctuation']:
                similar_term, similar_abbr = self.find_most_similar_term(word)
                new_abbr = self.openai_client.generate_ai_recommendations(word, similar_term, similar_abbr)
                print(f"신규 약어 생성: {word} → {new_abbr}")
                abbr.append(new_abbr)
        # sheet1의 약어 리스트 중 일치하는 약어 유무 파악
        matched_abbr = self.find_permutation_match(abbr, self.sheet1_abbr_list)
        if matched_abbr:
            abbr = [matched_abbr]
            print("기존 약어 사용")
        else:
            print("신규 약어 사용")
        return '_'.join(abbr)