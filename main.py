import logging
from typing import Dict, List, Tuple, Optional
from data_loader import DataLoader
from openai_client import OpenAIClient
from term_processor import TermProcessor

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TermRecommendationSystem:
    """용어 추천 시스템 메인 클래스"""
    
    def __init__(self, credentials_path: Optional[str] = None):
        self.data_loader = DataLoader(credentials_path)
        self.openai_client = OpenAIClient()
        self.term_processor = TermProcessor(self.openai_client, self.data_loader)  # data_loader 추가
        
    def load_data(self) -> Tuple[List[Dict], List[Dict]]:
        """데이터 로드"""
        logger.info("📊 데이터 로드 중...")
        return self.data_loader.load_data()

    def improve_term_definition(self, term_abbr: str) -> Dict:
        """용어 정의 개선"""
        terms, _ = self.load_data()
        return self.term_processor.improve_term_definition(term_abbr, terms)

    def recommend_abbreviation(self, search_query: str) -> List[str]:
        """약어 추천"""
        return self.term_processor.recommend_abbreviation(search_query)

def display_menu():
    """메뉴 표시"""
    print("\n" + "="*50)
    print("🏢 용어 추천 시스템")
    print("="*50)
    print("1. 용어 정의 개선")
    print("2. 약어 추천")
    print("3. 시스템 종료")
    print("-" * 50)

def improve_term_interactive(system):
    """용어 정의 개선 - 인터랙티브"""
    print("\n📝 용어 정의 개선")
    print("=" * 30)
    
    while True:
        term_abbr = input("개선할 용어의 약어를 입력하세요 (예: API_USE_YN) [뒤로가기: 'back']: ").strip()
        
        if term_abbr.lower() == 'back':
            break
        
        if not term_abbr:
            print("❌ 약어를 입력해주세요.")
            continue
            
        print(f"\n🔍 '{term_abbr}' 용어 정의를 개선 중...")
        print("-" * 30)
        
        try:
            result = system.improve_term_definition(term_abbr)
            
            if result.get('success'):
                print("✅ 정의 개선 완료!")
                print(f"\n📌 용어 약어: {term_abbr}")
                print(f"📝 원본 정의:")
                print(f"   {result.get('current_definition', '')}")
                print(f"\n✨ 개선된 정의:")
                print(f"   {result.get('improved_definition', '')}")
            else:
                print("❌ 정의 개선 실패!")
                print(f"사유: {result.get('message', '')}")
                
                # 디버깅 정보 제공
                if 'available_columns' in result:
                    print(f"\n💡 사용 가능한 컬럼: {result['available_columns']}")
                if 'sample_terms' in result:
                    print(f"💡 샘플 용어들: {result['sample_terms'][:5]}")
                    
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
        
        # 계속할지 묻기
        continue_choice = input("\n다른 용어도 개선하시겠습니까? (y/n): ").strip().lower()
        if continue_choice != 'y':
            break

def recommend_abbreviation_interactive(system):
    """약어 추천 - 인터랙티브"""
    print("\n🎯 약어 추천")
    print("=" * 30)
    
    while True:
        search_query = input("약어를 생성할 텍스트를 입력하세요 (예: 계좌번호) [뒤로가기: 'back']: ").strip()
        
        if search_query.lower() == 'back':
            break
        
        if not search_query:
            print("❌ 텍스트를 입력해주세요.")
            continue
            
        print(f"\n🔍 '{search_query}'에 대한 약어를 추천 중...")
        print("-" * 30)
        
        try:
            recommendations = system.recommend_abbreviation(search_query)
            
            if recommendations:
                print("✅ 약어 추천 완료!")
                print(f"📌 입력 텍스트: {search_query}")
                print(f"🎯 추천 약어: {recommendations}")
            else:
                print("❌ 약어 추천에 실패했습니다.")
                
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
        
        # 계속할지 묻기
        continue_choice = input("\n다른 텍스트의 약어도 추천받으시겠습니까? (y/n): ").strip().lower()
        if continue_choice != 'y':
            break

def main():
    """메인 실행 함수 - 인터랙티브 버전"""
    logger = logging.getLogger(__name__)
    
    try:
        print("🚀 시스템을 초기화하는 중입니다...")
        system = TermRecommendationSystem()
        print("✅ 시스템 초기화가 완료되었습니다!")
        
        while True:
            display_menu()
            choice = input("원하는 기능을 선택하세요 (1-3): ").strip()
            
            if choice == '1':
                improve_term_interactive(system)
            elif choice == '2':
                recommend_abbreviation_interactive(system)
            elif choice == '3':
                print("\n👋 시스템을 종료합니다. 이용해 주셔서 감사합니다!")
                break
            else:
                print("❌ 올바른 번호를 선택해주세요 (1-3)")
        
    except KeyboardInterrupt:
        print("\n\n👋 사용자에 의해 시스템이 종료되었습니다.")
    except Exception as e:
        logger.error(f"시스템 실행 중 오류 발생: {e}")
        print(f"❌ 시스템 오류: {e}")
        print("🔧 문제가 지속되면 관리자에게 문의해주세요.")

if __name__ == "__main__":
    main()