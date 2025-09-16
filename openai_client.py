import openai
import logging
from typing import Optional, List
from config import OPENAI_API_KEY, OPENAI_CONFIG_IMP, OPENAI_CONFIG_REC
import re

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self, api_key: str = OPENAI_API_KEY):
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
    
    def improve_ai_definition(self, term_abbr: str, term_name: str, current_definition: str) -> Optional[str]:
        """정의 개선용 OpenAI 호출"""
        prompt = f"""개발자들이 DB를 구성할 때 사용하는 컬럼 이름에 대한 정의를 개선해주세요. \"\"\"개선된 내용만 보여주세요.\"\"\"

            공통표준용어영문약어명: {term_abbr}
            공통표준용어명: {term_name}
            현재 정의: {current_definition}

            조건:
            - 문장은 개조식으로 끝나야 함 (예: "~여부.", "~번호.", "~명.", "~일자.")
            - 해당 컬럼이 어떤 것을 의미하는지 간단하게 설명
            - 누구나 이해할 수 있도록 작성
            - 개발자들이 경험적으로 사용하는 컬럼명 기준으로 설명
            - 200-250자 내외로 간결하게 작성
            - 양식은 지정되어 있습니다. 정의된 내용 만 보여주세요."""

        try:
            logger.info('🤖 OpenAI API 호출 중...')
            response = self.client.chat.completions.create(
                model=OPENAI_CONFIG_IMP['model'],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=OPENAI_CONFIG_IMP['max_tokens'],
                temperature=OPENAI_CONFIG_IMP['temperature']
            )

            if response:
                logger.info('✅ AI 응답 성공')
                return response.choices[0].message.content.strip()
            else:
                logger.info('❌ AI 응답 실패 - None 반환')
                return None
                
        except Exception as e:
            logger.error(f'❌ OpenAI 호출 중 오류: {e}')
            return None

    def generate_ai_recommendations(self, word: str, similar_terms: List[str], similar_abbrs: List[str]) -> str:
        """OpenAI GPT로 약어 생성 - 유사 용어가 있으면 선택, 없으면 새로 생성"""
        
        if len(similar_terms)>0:
            # 유사한 용어들이 있는 경우 - 가장 적합한 것 선택
            similar_terms_str = ", ".join(similar_terms)
            prompt = (
                f"'{word}'와 의미상 가장 유사한 용어를 아래 목록에서 선택해줘. "
                f"정확히 일치하는 의미의 용어가 있으면 그것을 선택하고, "
                f"없으면 'NONE'이라고 답해줘.\n\n"
                f"용어 목록: {similar_terms_str}\n\n"
                f"선택된 용어만 출력:"
            )
        else:
            # 유사한 용어가 없는 경우 - 새로 생성
            prompt = (
                f"다음 단어를 영문 약어로 변환해줘. "
                f"예시: '로그인' -> LGN, '일자' -> YMD, '번호' -> NO, '파일경로' -> FILE_PATH, '사용자' -> USER, '2024년' -> 2024, "
                f"한글 단어는 의미에 맞는 영문 약어로, 숫자는 그대로 출력. "
                f"아래 단어의 약어만 출력:\n{word}"
            )
        
        try:
            logger.info('🤖 OpenAI API 호출 중...')
            response = self.client.chat.completions.create(
                model=OPENAI_CONFIG_REC['model'],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=OPENAI_CONFIG_REC['max_tokens'],
                temperature=OPENAI_CONFIG_REC['temperature']
            )

            if response:
                logger.info('✅ AI 응답 성공')
                result = response.choices[0].message.content.strip()
                
                if len(similar_terms) > 0 and result in similar_terms:
                    # 유사 용어 중에서 선택된 경우
                    logger.info(f'📋 기존 용어 선택: {result}')
                    return similar_abbrs[similar_terms.index(result)]
                elif len(similar_terms) > 0 and result == 'NONE':
                    # 적합한 용어가 없다고 판단한 경우 - 새로 생성
                    logger.info('🆕 적합한 기존 용어 없음, 새로 생성')
                    return self.generate_ai_recommendations(word, [], [])  # 빈 리스트로 재귀 호출
                else:
                    # 새로 생성된 약어
                    abbr = re.sub(r'[^A-Z0-9_]', '', result)
                    logger.info(f'🆕 새 약어 생성: {abbr}')
                    return abbr
            else:
                logger.info('❌ AI 응답 실패 - None 반환')
                return None
                
        except Exception as e:
            logger.error(f'❌ OpenAI 호출 중 오류: {e}')
            return None
        
    def test_connection(self) -> bool:
        """OpenAI API 연결 테스트"""
        try:
            logger.info('🤖 OpenAI API 테스트 시작...')
            
            result = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": "안녕하세요. 테스트입니다."}],
                        max_tokens=20,
                        temperature=0.2
                    )
            if result:
                logger.info('✅ OpenAI API 연결 성공')
                logger.info(f'응답: {result}')
                return True
            else:
                logger.error('❌ OpenAI API 오류: 응답 없음')
                return False
                
        except Exception as e:
            logger.error(f'❌ OpenAI API 테스트 실패: {e}')
            return False