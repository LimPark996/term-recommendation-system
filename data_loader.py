import pandas as pd
import gspread
from typing import Dict, List, Tuple, Optional
import logging
from config import SPREADSHEET_ID, FILE_PATH
import numpy as np

logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, credentials_path: Optional[str] = None):
        self.credentials_path = credentials_path
        self.gc = None
        self._setup_credentials()
    
    def _setup_credentials(self):
        """Google Sheets API 인증 설정"""
        try:
            print("📡 Google Sheets 연결 중...")
            print("🔐 브라우저가 열리면 Google 계정으로 로그인해주세요.")

            # OAuth 인증
            self.gc = gspread.oauth(
                scopes=[
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ],
            credentials_filename='credentials.json',  # 현재 폴더의 파일 사용
            authorized_user_filename='token.json'     # 현재 폴더에 토큰 저장
            )
            print("✅ 인증 완료!")
        except Exception as e:
            print(f"❌ 인증 실패: {e}")        
            self.gc = None
    
    def read_spreadsheet_data(self, spreadsheet_id: str = SPREADSHEET_ID) -> Dict:
        """스프레드시트 데이터 읽기"""
        try:
            logger.info(f"📁 스프레드시트 읽는 중: {spreadsheet_id}")
            self.spreadsheet = self.gc.open_by_key(spreadsheet_id)
            print(f"📋 스프레드시트 열기 성공: {self.spreadsheet.title}")

            result = {}
            worksheets = self.spreadsheet.worksheets()

            for index, worksheet in enumerate(worksheets):
                sheet_name = worksheet.title

                try:
                    all_values = worksheet.get_all_values()

                    if not all_values:
                        logger.warning(f"⚠️ {sheet_name}: 데이터 없음")
                        continue

                    headers = all_values[0]
                    rows = all_values[1:]

                    df = pd.DataFrame(rows, columns=headers)
                    df = df.dropna(how='all')
                    df = df[df.astype(str).apply(lambda x: x.str.strip()).ne('').any(axis=1)]

                    logger.info(f"📊 {sheet_name}: {len(df)}행")
                    logger.info(f"📋 {sheet_name} 헤더: {headers}")

                    result[f'sheet{index + 1}'] = {
                        'name': sheet_name,
                        'headers': headers,
                        'data': df.to_dict('records')
                    }

                    logger.info(f"✅ {sheet_name}: {len(df)}개 유효 데이터 로드")

                except Exception as e:
                    logger.error(f"❌ {sheet_name} 처리 실패: {e}")
                    continue

            return result

        except Exception as e:
            logger.error(f"❌ 스프레드시트 읽기 실패: {e}")
            raise
    
    def load_data(self) -> Tuple[List[Dict], List[Dict]]:
        """데이터 로드 메인 함수"""
        spreadsheet_data = self.read_spreadsheet_data()
        
        if not spreadsheet_data:
            raise Exception('스프레드시트 데이터를 읽을 수 없습니다.')
        
        # Sheet1: 용어사전으로 가정
        sheet1 = spreadsheet_data.get('sheet1')
        if not sheet1:
            raise Exception('첫 번째 시트를 찾을 수 없습니다.')
        
        logger.info('\n📋 Sheet1 (용어사전) 정보:')
        logger.info(f'헤더: {sheet1["headers"]}')
        logger.info(f'데이터 수: {len(sheet1["data"])}')
        
        terms = sheet1['data']
        
        # Sheet2: 단어사전으로 가정
        sheet2 = spreadsheet_data.get('sheet2')
        words = []
        
        if sheet2:
            logger.info('\n📋 Sheet2 (단어사전) 정보:')
            logger.info(f'헤더: {sheet2["headers"]}')
            logger.info(f'데이터 수: {len(sheet2["data"])}')

            words = sheet2['data']
        else:
            logger.info('\n⚠️ 두 번째 시트가 없습니다. 단어사전을 사용하지 않습니다.')
        
        logger.info(f'\n✅ 데이터 로드 완료: 용어 {len(terms)}개, 단어 {len(words)}개')
        
        return terms, words

    def load_data_rec(self, terms: List[Dict], words: List[Dict]) -> Tuple[List[str], List[str], List[str], List[np.ndarray]]:
        sheet1_abbr_list = []
        term_data = []
        abbr_data = []
        term_embeddings = self.load_embeddings_from_excel(FILE_PATH)

        # terms 처리
        for term in terms:
            keys = list(term.keys())
            if len(keys) > 3:
                abbr_key = keys[3]  # 4번째 키
                sheet1_abbr_list.append(str(term[abbr_key]).strip())
                
        # words 처리 - Dict 키로 접근
        for row in words:
            keys = list(row.keys())
            if len(keys) < 2:
                continue
            
            term_key = keys[0]  # 첫 번째 키
            abbr_key = keys[1]  # 두 번째 키
            
            term = str(row[term_key]).strip()
            abbr = str(row[abbr_key]).strip()
            
            term_data.append(term)
            abbr_data.append(abbr)
        return sheet1_abbr_list, term_data, abbr_data, term_embeddings

    def load_embeddings_from_excel(self, excel_path: str, sheet_name: str = "공통표준단어", column_name: str = "embedding") -> List[np.ndarray]:
        print(f"엑셀 파일 경로: {excel_path}")
        
        try:
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            print(f"데이터프레임 shape: {df.shape}")
            
            embeddings = []
            dimension_stats = {}
            problematic_indices = []
            
            for i, emb_str in enumerate(df[column_name].dropna()):
                emb_str = str(emb_str).strip()
                
                if emb_str and emb_str != '-' and ',' in emb_str:
                    try:
                        emb_array = [float(x.strip()) for x in emb_str.split(',')]
                        emb = np.array(emb_array)
                        dimension = len(emb)
                        
                        # 차원별 통계
                        if dimension not in dimension_stats:
                            dimension_stats[dimension] = []
                        dimension_stats[dimension].append(i)
                        
                        # 1536이 아닌 차원들 기록
                        if dimension != 1536:
                            problematic_indices.append((i, dimension))
                        
                        embeddings.append(emb)
                        
                    except ValueError as e:
                        print(f"행 {i} 파싱 에러: {e}")
                        embeddings.append(None)
                else:
                    embeddings.append(None)
            
            # 차원 분석 결과 출력
            print("\n=== Embedding 차원 분석 ===")
            for dim, indices in sorted(dimension_stats.items()):
                print(f"{dim}차원: {len(indices)}개")
                if dim != 1536:
                    print(f"  예시 인덱스: {indices[:10]}")  # 처음 10개만 표시
            
            if problematic_indices:
                print(f"\n문제있는 embedding들 ({len(problematic_indices)}개):")
                for idx, dim in problematic_indices[:20]:  # 처음 20개만 표시
                    print(f"  행 {idx}: {dim}차원")
                if len(problematic_indices) > 20:
                    print(f"  ... 외 {len(problematic_indices) - 20}개 더")
            else:
                print("모든 embedding이 정상적으로 1536차원입니다.")
            
            print(f"\n총 {len(embeddings)}개 embedding 로드 완료")
            return embeddings
            
        except Exception as e:
            print(f"예외 발생: {type(e).__name__}: {e}")
            return []
        
    def check_spreadsheet_access(self, spreadsheet_id: str = SPREADSHEET_ID) -> bool:
        """스프레드시트 접근 권한 확인"""
        try:
            logger.info('📋 스프레드시트 접근 테스트 시작...')
            
            try:
                spreadsheet = self.gc.open_by_key(spreadsheet_id)
                logger.info(f'✅ ID로 스프레드시트 접근 성공: {spreadsheet.title}')
            except Exception as e:
                logger.info('⚠️ ID 접근 실패, 첫 번째 스프레드시트 사용')
                spreadsheets = self.gc.openall()
                if spreadsheets:
                    spreadsheet = spreadsheets[0]
                    logger.info(f'✅ 첫 번째 스프레드시트 접근 성공: {spreadsheet.title}')
                else:
                    raise Exception("접근 가능한 스프레드시트가 없습니다")
            
            worksheets = spreadsheet.worksheets()
            logger.info(f'📊 시트 개수: {len(worksheets)}')
            
            for index, worksheet in enumerate(worksheets):
                name = worksheet.title
                rows = worksheet.row_count
                cols = worksheet.col_count
                logger.info(f'시트 {index + 1}: {name} ({rows}행 x {cols}열)')
                
                if rows > 0:
                    try:
                        headers = worksheet.row_values(1)
                        logger.info(f'헤더: {", ".join(headers)}')
                    except:
                        pass
            
            return True
            
        except Exception as e:
            logger.error(f'❌ 스프레드시트 접근 실패: {e}')
            return False