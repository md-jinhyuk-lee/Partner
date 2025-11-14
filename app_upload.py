import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from io import BytesIO

# 페이지 설정
st.set_page_config(
    page_title="파트너 정산 관리",
    page_icon="💰",
    layout="wide"
)

# 세션 스테이트 초기화
if 'df_prices' not in st.session_state:
    st.session_state.df_prices = pd.DataFrame()
if 'df_stores' not in st.session_state:
    st.session_state.df_stores = pd.DataFrame()
if 'df_usage' not in st.session_state:
    st.session_state.df_usage = pd.DataFrame()
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 이메일 설정 (기본값)
DEFAULT_SENDER_EMAIL = "dlwlsgur85@gmail.com"
DEFAULT_SENDER_PASSWORD = "lpmu cclo ftnc yvam"

# 제목
st.title("💰 파트너 정산 관리 시스템")
st.markdown("### 부자재 · 택배 · 행낭 사용 비용 자동 정산")

# 사이드바 - 패스워드
with st.sidebar:
    st.header("🔐 로그인")
    
    if not st.session_state.authenticated:
        password = st.text_input("패스워드", type="password", key="password_input")
        
        if st.button("로그인", use_container_width=True):
            if password == "dy1234":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ 패스워드가 틀렸습니다")
        st.stop()
    else:
        st.success("✅ 인증 완료")
        if st.button("로그아웃", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
    
    st.divider()
    
    # 데이터 초기화 버튼
    if st.button("🗑️ 전체 데이터 초기화", use_container_width=True, type="secondary"):
        st.session_state.df_prices = pd.DataFrame()
        st.session_state.df_stores = pd.DataFrame()
        st.session_state.df_usage = pd.DataFrame()
        st.success("데이터가 초기화되었습니다!")
        st.rerun()
    
    st.divider()
    
    # 이메일 설정 정보
    st.markdown("### 📧 이메일 설정")
    
    with st.expander("📧 현재 이메일 설정 보기/수정"):
        st.write("**현재 설정:**")
        st.code(f"Gmail: {DEFAULT_SENDER_EMAIL}")
        st.code(f"비밀번호: {DEFAULT_SENDER_PASSWORD}")
        
        st.markdown("---")
        st.warning("⚠️ 이메일 설정을 변경하려면 코드를 직접 수정해야 합니다.")
        st.info("""
        **변경 방법:**
        1. GitHub에서 app_v3.1.py 파일 열기
        2. 14-15번째 줄 수정:
        ```python
        DEFAULT_SENDER_EMAIL = "새이메일@gmail.com"
        DEFAULT_SENDER_PASSWORD = "새비밀번호"
        ```
        3. Commit → 자동 재배포
        """)
    
    st.success("✅ 이메일 발송 시 자동으로 위 설정이 사용됩니다")
    
    st.divider()
    
    st.markdown("""
    ### 📝 CSV 형식
    
    **단가관리.csv**
    ```
    품목명,단가,카테고리
    비닐봉투(소),50,부자재
    택배,3000,택배
    ```
    
    **매장관리.csv**
    ```
    매장명,매장코드
    강남점,GN01
    ```
    
    **사용내역.csv**
    ```
    날짜,매장명,품목명,수량
    2024-11-01,강남점,비닐봉투(소),50
    ```
    
    💡 **기존 데이터에 추가됩니다!**
    """)

# CSV 로드 함수
def load_csv_with_encoding(file):
    """다양한 인코딩으로 CSV 로드 시도"""
    for encoding in ['utf-8', 'cp949', 'euc-kr']:
        try:
            file.seek(0)
            df = pd.read_csv(file, encoding=encoding)
            df.columns = df.columns.str.strip()
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].str.strip()
            return df
        except:
            continue
    return None

# 메인 영역
st.header("📤 파일 업로드")

col1, col2, col3 = st.columns(3)

# 단가관리 업로드
with col1:
    st.subheader("💰 단가관리")
    price_file = st.file_uploader(
        "단가관리 CSV 파일",
        type=['csv'],
        key="price_file",
        help="품목명, 단가, 카테고리"
    )
    
    if price_file:
        df_new = load_csv_with_encoding(price_file)
        if df_new is not None:
            # 필수 컬럼 확인
            if all(col in df_new.columns for col in ['품목명', '단가', '카테고리']):
                df_new['단가'] = pd.to_numeric(df_new['단가'], errors='coerce')
                df_new = df_new.dropna(subset=['단가'])
                
                # 기존 데이터와 병합 (중복 제거)
                if not st.session_state.df_prices.empty:
                    st.session_state.df_prices = pd.concat([st.session_state.df_prices, df_new]).drop_duplicates(subset=['품목명'], keep='last').reset_index(drop=True)
                else:
                    st.session_state.df_prices = df_new
                
                st.success(f"✅ {len(df_new)}개 품목 추가 (총 {len(st.session_state.df_prices)}개)")
            else:
                st.error("❌ 필수 컬럼: 품목명, 단가, 카테고리")
    
    if not st.session_state.df_prices.empty:
        st.info(f"현재 {len(st.session_state.df_prices)}개 품목 등록됨")

# 매장관리 업로드
with col2:
    st.subheader("🏪 매장관리")
    store_file = st.file_uploader(
        "매장관리 CSV 파일",
        type=['csv'],
        key="store_file",
        help="매장명, 매장코드"
    )
    
    if store_file:
        df_new = load_csv_with_encoding(store_file)
        if df_new is not None:
            if all(col in df_new.columns for col in ['매장명', '매장코드']):
                # 기존 데이터와 병합 (중복 제거)
                if not st.session_state.df_stores.empty:
                    st.session_state.df_stores = pd.concat([st.session_state.df_stores, df_new]).drop_duplicates(subset=['매장코드'], keep='last').reset_index(drop=True)
                else:
                    st.session_state.df_stores = df_new
                
                st.success(f"✅ {len(df_new)}개 매장 추가 (총 {len(st.session_state.df_stores)}개)")
            else:
                st.error("❌ 필수 컬럼: 매장명, 매장코드")
    
    if not st.session_state.df_stores.empty:
        st.info(f"현재 {len(st.session_state.df_stores)}개 매장 등록됨")

# 사용내역 업로드
with col3:
    st.subheader("📊 사용내역")
    usage_file = st.file_uploader(
        "사용내역 CSV 파일",
        type=['csv'],
        key="usage_file",
        help="날짜, 매장명(또는 매장코드), 품목명, 수량"
    )
    
    if usage_file:
        df_new = load_csv_with_encoding(usage_file)
        if df_new is not None:
            has_store = '매장코드' in df_new.columns or '매장명' in df_new.columns
            has_required = all(col in df_new.columns for col in ['날짜', '품목명', '수량'])
            
            if has_store and has_required:
                df_new['수량'] = pd.to_numeric(df_new['수량'], errors='coerce')
                df_new = df_new.dropna(subset=['수량'])
                
                # 기존 데이터와 병합
                if not st.session_state.df_usage.empty:
                    st.session_state.df_usage = pd.concat([st.session_state.df_usage, df_new]).reset_index(drop=True)
                else:
                    st.session_state.df_usage = df_new
                
                st.success(f"✅ {len(df_new)}건 추가 (총 {len(st.session_state.df_usage)}건)")
            else:
                st.error("❌ 필수 컬럼: 날짜, 매장명(또는 매장코드), 품목명, 수량")
    
    if not st.session_state.df_usage.empty:
        st.info(f"현재 {len(st.session_state.df_usage)}건 등록됨")

st.divider()

# 정산 계산
if not st.session_state.df_prices.empty and not st.session_state.df_stores.empty and not st.session_state.df_usage.empty:
    st.header("📊 정산 결과")
    
    df_prices = st.session_state.df_prices
    df_stores = st.session_state.df_stores
    df_usage = st.session_state.df_usage
    
    # 사용내역에 카테고리 추가 (단가 정보와 조인)
    df_usage_with_category = df_usage.merge(
        df_prices[['품목명', '카테고리', '단가']],
        on='품목명',
        how='left'
    )
    
    # 매장명 통일 (매장코드로 매칭)
    use_store_code = '매장코드' in df_usage.columns
    
    settlements = []
    category_summary = []
    total_amount = 0
    
    for _, store in df_stores.iterrows():
        store_code = store['매장코드']
        store_name = store['매장명']
        
        # 해당 매장의 사용내역 필터링
        if use_store_code:
            store_usage = df_usage_with_category[df_usage_with_category['매장코드'] == store_code]
        else:
            store_usage = df_usage_with_category[df_usage_with_category['매장명'] == store_name]
        
        if not store_usage.empty:
            store_total = 0
            items_detail = []
            category_totals = {}
            
            for _, usage in store_usage.iterrows():
                try:
                    item_name = usage['품목명']
                    quantity = usage['수량']
                    unit_price = usage['단가']
                    category = usage['카테고리']
                    
                    if pd.notna(unit_price):
                        subtotal = unit_price * quantity
                        store_total += subtotal
                        
                        # 카테고리별 집계
                        if category not in category_totals:
                            category_totals[category] = {'수량': 0, '금액': 0}
                        category_totals[category]['수량'] += quantity
                        category_totals[category]['금액'] += subtotal
                        
                        items_detail.append({
                            '날짜': usage['날짜'],
                            '품목명': item_name,
                            '카테고리': category,
                            '수량': int(quantity) if quantity == int(quantity) else quantity,
                            '단가': int(unit_price) if unit_price == int(unit_price) else unit_price,
                            '금액': int(subtotal) if subtotal == int(subtotal) else subtotal
                        })
                except:
                    continue
            
            if items_detail:
                settlements.append({
                    '매장명': store_name,
                    '매장코드': store_code,
                    '상세내역': items_detail,
                    '카테고리별': category_totals,
                    '합계': store_total
                })
                total_amount += store_total
                
                # 전체 카테고리 요약용
                for cat, data in category_totals.items():
                    category_summary.append({
                        '매장명': store_name,
                        '카테고리': cat,
                        '수량': data['수량'],
                        '금액': data['금액']
                    })
    
    # 요약 통계
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("등록 품목", f"{len(df_prices)}개")
    
    with col2:
        st.metric("등록 매장", f"{len(df_stores)}개")
    
    with col3:
        st.metric("사용 건수", f"{len(df_usage)}건")
    
    with col4:
        st.metric("전체 정산 금액", f"{int(total_amount):,}원")
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 30px; border-radius: 15px; margin: 30px 0;'>
        <h2 style='color: white; margin: 0;'>💵 전체 정산 금액</h2>
        <h1 style='color: white; margin: 10px 0 0 0; font-size: 52px;'>
            {int(total_amount):,}원
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # 1. 매장별 정산 내역 (요약)
    st.subheader("📊 매장별 정산 내역")
    
    # 필터 추가
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        selected_stores_summary = st.multiselect(
            "매장 필터",
            options=df_stores['매장명'].unique().tolist(),
            default=df_stores['매장명'].unique().tolist(),
            key="summary_store_filter"
        )
    with col_f2:
        selected_categories_summary = st.multiselect(
            "카테고리 필터",
            options=df_prices['카테고리'].unique().tolist(),
            default=df_prices['카테고리'].unique().tolist(),
            key="summary_category_filter"
        )
    
    # 필터링된 데이터
    category_summary_filtered = [
        item for item in category_summary 
        if item['매장명'] in selected_stores_summary and item['카테고리'] in selected_categories_summary
    ]
    
    df_category_summary = pd.DataFrame(category_summary_filtered)
    
    if not df_category_summary.empty:
        # 피벗 테이블로 보기 좋게 변환
        pivot_summary = df_category_summary.pivot_table(
            index='매장명',
            columns='카테고리',
            values=['수량', '금액'],
            aggfunc='sum',
            fill_value=0
        )
        
        # MultiIndex 컬럼을 2단 헤더 형식의 데이터프레임으로 변환
        summary_display = []
        for store_name in pivot_summary.index:
            row_data = {'매장명': store_name}
            store_total = 0
            
            for category in df_prices['카테고리'].unique():
                if ('수량', category) in pivot_summary.columns:
                    qty = pivot_summary.loc[store_name, ('수량', category)]
                    amt = pivot_summary.loc[store_name, ('금액', category)]
                    # 카테고리별로 수량과 금액을 함께 표시
                    row_data[f'{category}'] = f"수량: {int(qty):,} | 금액: {int(amt):,}원"
                    store_total += amt
                else:
                    row_data[f'{category}'] = f"수량: 0 | 금액: 0원"
            
            row_data['합계'] = f"{int(store_total):,}원"
            summary_display.append(row_data)
        
        df_summary_display = pd.DataFrame(summary_display)
        
        # HTML로 커스텀 테이블 생성 (더 보기 좋게)
        html_table = """
        <style>
            .summary-table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .summary-table th {
                background-color: #FFF9E6;
                border: 2px solid #333;
                padding: 12px 8px;
                text-align: center;
                font-weight: bold;
                color: #333;
            }
            .summary-table .header-category {
                background-color: #FFF9E6;
                font-size: 15px;
            }
            .summary-table .header-metric {
                background-color: #FFFBF0;
                font-size: 13px;
                color: #666;
            }
            .summary-table td {
                border: 1px solid #ddd;
                padding: 10px 8px;
                text-align: center;
            }
            .summary-table .store-col {
                background-color: #F5F5F5;
                font-weight: bold;
                text-align: left;
            }
            .summary-table .total-col {
                background-color: #E8F4F8;
                font-weight: bold;
                color: #0066CC;
                font-size: 16px;
            }
            .summary-table .qty-cell {
                color: #333;
                font-size: 14px;
            }
            .summary-table .amt-cell {
                color: #0066CC;
                font-weight: 500;
                font-size: 14px;
            }
        </style>
        <table class="summary-table">
            <thead>
                <tr>
                    <th rowspan="2" class="header-category">매장명</th>
        """
        
        # 카테고리 헤더 (1행)
        for category in df_prices['카테고리'].unique():
            html_table += f'<th colspan="2" class="header-category">{category}</th>'
        html_table += '<th rowspan="2" class="header-category">합계</th></tr><tr>'
        
        # 수량/금액 헤더 (2행)
        for category in df_prices['카테고리'].unique():
            html_table += '<th class="header-metric">수량</th><th class="header-metric">금액</th>'
        html_table += '</tr></thead><tbody>'
        
        # 데이터 행
        for store_name in pivot_summary.index:
            html_table += f'<tr><td class="store-col">{store_name}</td>'
            store_total = 0
            
            for category in df_prices['카테고리'].unique():
                if ('수량', category) in pivot_summary.columns:
                    qty = pivot_summary.loc[store_name, ('수량', category)]
                    amt = pivot_summary.loc[store_name, ('금액', category)]
                    html_table += f'<td class="qty-cell">{int(qty):,}</td><td class="amt-cell">{int(amt):,}원</td>'
                    store_total += amt
                else:
                    html_table += '<td class="qty-cell">0</td><td class="amt-cell">0원</td>'
            
            html_table += f'<td class="total-col">{int(store_total):,}원</td></tr>'
        
        html_table += '</tbody></table>'
        
        st.markdown(html_table, unsafe_allow_html=True)
    
    st.divider()
    
    # 2. 매장별 정산 상세 내역
    st.subheader("🏪 매장별 정산 상세 내역")
    
    # 필터 추가
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        selected_stores_detail = st.multiselect(
            "매장 필터",
            options=df_stores['매장명'].unique().tolist(),
            default=df_stores['매장명'].unique().tolist(),
            key="detail_store_filter"
        )
    with col_f2:
        selected_categories_detail = st.multiselect(
            "카테고리 필터",
            options=df_prices['카테고리'].unique().tolist(),
            default=df_prices['카테고리'].unique().tolist(),
            key="detail_category_filter"
        )
    with col_f3:
        # 날짜 필터 (선택사항)
        if not df_usage.empty and '날짜' in df_usage.columns:
            all_dates = pd.to_datetime(df_usage['날짜'], errors='coerce').dropna()
            if not all_dates.empty:
                date_filter_enabled = st.checkbox("날짜 필터 사용", key="date_filter_enabled")
                if date_filter_enabled:
                    min_date = all_dates.min().date()
                    max_date = all_dates.max().date()
                    date_range = st.date_input(
                        "날짜 범위",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date,
                        key="date_range_filter"
                    )
                else:
                    date_range = None
            else:
                date_range = None
        else:
            date_range = None
    
    # 필터링된 settlements
    settlements_filtered = [
        s for s in settlements 
        if s['매장명'] in selected_stores_detail
    ]
    
    for settlement in settlements_filtered:
        # 카테고리와 날짜 필터 적용
        items_filtered = []
        for item in settlement['상세내역']:
            # 카테고리 필터
            if item['카테고리'] not in selected_categories_detail:
                continue
            
            # 날짜 필터
            if date_range and len(date_range) == 2:
                try:
                    item_date = pd.to_datetime(item['날짜']).date()
                    if not (date_range[0] <= item_date <= date_range[1]):
                        continue
                except:
                    pass
            
            items_filtered.append(item)
        
        if items_filtered:
            filtered_total = sum(item['금액'] for item in items_filtered)
            
            with st.expander(
                f"**{settlement['매장명']}** ({settlement['매장코드']}) - **{int(filtered_total):,}원**",
                expanded=True
            ):
                df_detail = pd.DataFrame(items_filtered)
                
                # 포맷팅
                df_detail['단가'] = df_detail['단가'].apply(lambda x: f"{int(x):,}원")
                df_detail['금액'] = df_detail['금액'].apply(lambda x: f"{int(x):,}원")
                
                st.dataframe(
                    df_detail,
                    use_container_width=True,
                    hide_index=True
                )
                
                # 매장 합계
                st.markdown(f"""
                <div style='background-color: #f0f0f0; padding: 15px; border-radius: 8px; margin-top: 10px;'>
                    <h3 style='margin: 0; text-align: right;'>
                        매장 합계 (필터 적용): <span style='color: #667eea;'>{int(filtered_total):,}원</span>
                    </h3>
                </div>
                """, unsafe_allow_html=True)
    
    st.divider()
    
    # 3. 전체 상세 내역
    st.subheader("📋 전체 상세 내역")
    
    # 필터 추가
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        selected_stores_all = st.multiselect(
            "매장 필터",
            options=df_stores['매장명'].unique().tolist(),
            default=df_stores['매장명'].unique().tolist(),
            key="all_store_filter"
        )
    with col_f2:
        selected_categories_all = st.multiselect(
            "카테고리 필터",
            options=df_prices['카테고리'].unique().tolist(),
            default=df_prices['카테고리'].unique().tolist(),
            key="all_category_filter"
        )
    with col_f3:
        all_items = []
        for settlement in settlements:
            for item in settlement['상세내역']:
                all_items.append(item['품목명'])
        unique_items = list(set(all_items))
        
        selected_items = st.multiselect(
            "품목 필터",
            options=sorted(unique_items),
            default=sorted(unique_items),
            key="all_item_filter"
        )
    with col_f4:
        # 날짜 필터 (선택사항)
        if not df_usage.empty and '날짜' in df_usage.columns:
            all_dates = pd.to_datetime(df_usage['날짜'], errors='coerce').dropna()
            if not all_dates.empty:
                date_filter_all_enabled = st.checkbox("날짜 필터 사용", key="date_filter_all_enabled")
                if date_filter_all_enabled:
                    min_date = all_dates.min().date()
                    max_date = all_dates.max().date()
                    date_range_all = st.date_input(
                        "날짜 범위",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date,
                        key="date_range_all_filter"
                    )
                else:
                    date_range_all = None
            else:
                date_range_all = None
        else:
            date_range_all = None
    
    export_data = []
    for settlement in settlements:
        if settlement['매장명'] not in selected_stores_all:
            continue
        
        for item in settlement['상세내역']:
            # 카테고리 필터
            if item['카테고리'] not in selected_categories_all:
                continue
            
            # 품목 필터
            if item['품목명'] not in selected_items:
                continue
            
            # 날짜 필터
            if date_range_all and len(date_range_all) == 2:
                try:
                    item_date = pd.to_datetime(item['날짜']).date()
                    if not (date_range_all[0] <= item_date <= date_range_all[1]):
                        continue
                except:
                    pass
            
            export_data.append({
                '매장명': settlement['매장명'],
                '매장코드': settlement['매장코드'],
                '날짜': item['날짜'],
                '품목명': item['품목명'],
                '카테고리': item['카테고리'],
                '수량': item['수량'],
                '단가': item['단가'],
                '금액': item['금액']
            })
    
    df_export = pd.DataFrame(export_data)
    
    if not df_export.empty:
        # 필터링된 총액 표시
        filtered_total_amount = df_export['금액'].sum()
        st.info(f"📊 필터링된 데이터: **{len(df_export)}건** | 총액: **{int(filtered_total_amount):,}원**")
        
        # 화면 표시용 (포맷팅)
        df_display = df_export.copy()
        df_display['단가'] = df_display['단가'].apply(lambda x: f"{int(x):,}원" if isinstance(x, (int, float)) else x)
        df_display['금액'] = df_display['금액'].apply(lambda x: f"{int(x):,}원" if isinstance(x, (int, float)) else x)
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ 필터 조건에 맞는 데이터가 없습니다.")
    
    st.divider()
    
    # 4. 다운로드 및 이메일 발송
    st.subheader("💾 다운로드 및 이메일 발송")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📥 XLSX 다운로드")
        
        download_filtered = st.checkbox("필터링된 데이터만 다운로드", value=False, key="download_filtered")
        
        # XLSX 파일 생성
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if download_filtered and not df_export.empty:
                # 필터링된 데이터
                # 매장별 정산 내역 (필터링)
                if not df_category_summary.empty:
                    pivot_summary = df_category_summary.pivot_table(
                        index='매장명',
                        columns='카테고리',
                        values=['수량', '금액'],
                        aggfunc='sum',
                        fill_value=0
                    )
                    
                    summary_display = []
                    for store_name in pivot_summary.index:
                        row = {'매장명': store_name}
                        store_total = 0
                        for category in selected_categories_summary:
                            if ('수량', category) in pivot_summary.columns:
                                qty = pivot_summary.loc[store_name, ('수량', category)]
                                amt = pivot_summary.loc[store_name, ('금액', category)]
                                row[f'{category}_수량'] = int(qty) if qty == int(qty) else qty
                                row[f'{category}_금액'] = int(amt)
                                store_total += amt
                        row['합계'] = int(store_total)
                        summary_display.append(row)
                    
                    pd.DataFrame(summary_display).to_excel(writer, sheet_name='매장별정산_필터링', index=False)
                
                # 전체 상세 내역 (필터링)
                df_export.to_excel(writer, sheet_name='상세내역_필터링', index=False)
            else:
                # 전체 데이터
                # 매장별 정산 내역 (전체)
                df_category_summary_all = pd.DataFrame(category_summary)
                if not df_category_summary_all.empty:
                    pivot_summary = df_category_summary_all.pivot_table(
                        index='매장명',
                        columns='카테고리',
                        values=['수량', '금액'],
                        aggfunc='sum',
                        fill_value=0
                    )
                    
                    summary_display = []
                    for store_name in pivot_summary.index:
                        row = {'매장명': store_name}
                        store_total = 0
                        for category in df_prices['카테고리'].unique():
                            if ('수량', category) in pivot_summary.columns:
                                qty = pivot_summary.loc[store_name, ('수량', category)]
                                amt = pivot_summary.loc[store_name, ('금액', category)]
                                row[f'{category}_수량'] = int(qty) if qty == int(qty) else qty
                                row[f'{category}_금액'] = int(amt)
                                store_total += amt
                        row['합계'] = int(store_total)
                        summary_display.append(row)
                    
                    pd.DataFrame(summary_display).to_excel(writer, sheet_name='매장별정산', index=False)
                
                # 전체 상세 내역
                export_data_all = []
                for settlement in settlements:
                    for item in settlement['상세내역']:
                        export_data_all.append({
                            '매장명': settlement['매장명'],
                            '매장코드': settlement['매장코드'],
                            '날짜': item['날짜'],
                            '품목명': item['품목명'],
                            '카테고리': item['카테고리'],
                            '수량': item['수량'],
                            '단가': item['단가'],
                            '금액': item['금액']
                        })
                pd.DataFrame(export_data_all).to_excel(writer, sheet_name='상세내역', index=False)
                
                # 각 매장별 시트
                for settlement in settlements:
                    df_store = pd.DataFrame(settlement['상세내역'])
                    sheet_name = settlement['매장명'][:31]  # Excel 시트명 길이 제한
                    df_store.to_excel(writer, sheet_name=sheet_name, index=False)
        
        excel_data = output.getvalue()
        
        file_suffix = "_필터링" if download_filtered else ""
        st.download_button(
            label=f"📥 정산 결과 다운로드{file_suffix} (XLSX)",
            data=excel_data,
            file_name=f"정산결과{file_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        st.markdown("#### 📧 이메일 발송")
        
        email_filtered = st.checkbox("필터링된 데이터만 발송", value=False, key="email_filtered")
        email_to = st.text_input("받는 사람 이메일", placeholder="example@email.com")
        
        if st.button("📧 매장별 정산 내역 이메일 발송", use_container_width=True):
            if email_to:
                # 사용할 데이터 결정
                if email_filtered and not df_category_summary.empty:
                    summary_data_for_email = df_category_summary
                    email_categories = selected_categories_summary
                    email_subject_suffix = " (필터링)"
                else:
                    summary_data_for_email = pd.DataFrame(category_summary)
                    email_categories = df_prices['카테고리'].unique()
                    email_subject_suffix = ""
                
                # 이메일 본문 생성 - 인라인 스타일 적용
                email_body = f"""
                <html>
                <head>
                    <meta charset="utf-8">
                </head>
                <body style="font-family: 'Malgun Gothic', Arial, sans-serif; color: #333; padding: 20px;">
                    <div style="background-color: white; padding: 30px;">
                        <h2 style="color: #333; margin: 0 0 10px 0;">🔥 파트너 정산 내역{email_subject_suffix}</h2>
                        <p style="margin: 5px 0;"><strong>정산 기간:</strong> {datetime.now().strftime('%Y-%m-%d')}</p>
"""
                
                if email_filtered and not df_export.empty:
                    filtered_email_total = df_export['금액'].sum()
                    email_body += f"<p style='margin: 5px 0;'><strong>전체 정산 금액 (필터 적용):</strong> {int(filtered_email_total):,}원</p>"
                else:
                    email_body += f"<p style='margin: 5px 0;'><strong>전체 정산 금액:</strong> {int(total_amount):,}원</p>"
                
                email_body += """
                        <h3 style="color: #333; margin: 30px 0 15px 0; font-size: 18px;">매장별 정산 내역</h3>
                        <table style="border-collapse: collapse; width: 100%; margin: 20px 0; font-size: 13px;">
"""
                
                # 2단 헤더 구조 - 완전한 인라인 스타일
                # 1행: 매장명(rowspan=2) + 각 카테고리(colspan=2) + 합계(rowspan=2)
                email_body += "<tr><th rowspan='2' style='border: 1px solid #000; padding: 10px 8px; text-align: center; font-weight: bold; background-color: #ffffff; color: #000; vertical-align: middle;'>매장명</th>"
                for category in email_categories:
                    email_body += f"<th colspan='2' style='border: 1px solid #000; padding: 10px 8px; text-align: center; font-weight: bold; background-color: #ffffff; color: #000;'>{category}</th>"
                email_body += "<th rowspan='2' style='border: 1px solid #000; padding: 10px 8px; text-align: center; font-weight: bold; background-color: #ffffff; color: #000; vertical-align: middle;'>합계</th></tr>"
                
                # 2행: 각 카테고리 아래 수량/금액
                email_body += "<tr>"
                for category in email_categories:
                    email_body += "<th style='border: 1px solid #000; padding: 10px 8px; text-align: center; font-weight: bold; background-color: #ffffff; color: #000; width: 70px;'>수량</th>"
                    email_body += "<th style='border: 1px solid #000; padding: 10px 8px; text-align: center; font-weight: bold; background-color: #ffffff; color: #000; width: 90px;'>금액</th>"
                email_body += "</tr>"
                
                # 피벗 테이블 생성
                if not summary_data_for_email.empty:
                    pivot_summary = summary_data_for_email.pivot_table(
                        index='매장명',
                        columns='카테고리',
                        values=['수량', '금액'],
                        aggfunc='sum',
                        fill_value=0
                    )
                    
                    # 데이터 행 추가 - 완전한 인라인 스타일
                    row_num = 0
                    for store_name in pivot_summary.index:
                        row_num += 1
                        # 짝수/홀수 행 배경색
                        bg_color = "#f8f9fa" if row_num % 2 == 0 else "#ffffff"
                        
                        email_body += f"<tr style='background-color: {bg_color};'>"
                        email_body += f"<td style='border: 1px solid #ddd; padding: 8px; text-align: left; color: #000; padding-left: 15px;'>{store_name}</td>"
                        
                        store_total = 0
                        for category in email_categories:
                            if ('수량', category) in pivot_summary.columns:
                                qty = pivot_summary.loc[store_name, ('수량', category)]
                                amt = pivot_summary.loc[store_name, ('금액', category)]
                                qty_display = f"{int(qty):,}" if qty > 0 else "0"
                                amt_display = f"{int(amt):,}원" if amt > 0 else "0원"
                                email_body += f"<td style='border: 1px solid #ddd; padding: 8px; text-align: center; color: #000;'>{qty_display}</td>"
                                email_body += f"<td style='border: 1px solid #ddd; padding: 8px; text-align: center; color: #0066CC; font-weight: normal;'>{amt_display}</td>"
                                store_total += amt
                            else:
                                email_body += "<td style='border: 1px solid #ddd; padding: 8px; text-align: center; color: #000;'>0</td>"
                                email_body += "<td style='border: 1px solid #ddd; padding: 8px; text-align: center; color: #0066CC; font-weight: normal;'>0원</td>"
                        
                        email_body += f"<td style='border: 1px solid #ddd; padding: 8px; text-align: center; font-weight: bold; color: #0066CC;'>{int(store_total):,}원</td></tr>"
                
                email_body += """
                        </table>
                        
                        <div style="margin-top: 30px; padding: 15px; background-color: #f8f9fa; border-left: 3px solid #0066CC; font-size: 12px; color: #666;">
                            <p style="margin: 5px 0;"><strong>첨부 파일:</strong> 정산 결과 XLSX 파일</p>
                            <p style="margin: 5px 0;"><strong>안내:</strong> 상세 내역은 첨부된 엑셀 파일을 확인해주세요.</p>
                            <p style="margin: 5px 0;"><strong>문의:</strong> 정산 내역 문의사항이 있으시면 연락 주시기 바랍니다.</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                try:
                    # 기본 이메일 설정 사용
                    sender_email = DEFAULT_SENDER_EMAIL
                    sender_password = DEFAULT_SENDER_PASSWORD.replace(" ", "")  # 공백 제거
                    
                    # XLSX 파일 생성
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        if email_filtered and not df_export.empty:
                            # 필터링된 데이터
                            if not df_category_summary.empty:
                                pivot_summary = df_category_summary.pivot_table(
                                    index='매장명',
                                    columns='카테고리',
                                    values=['수량', '금액'],
                                    aggfunc='sum',
                                    fill_value=0
                                )
                                
                                summary_display = []
                                for store_name in pivot_summary.index:
                                    row = {'매장명': store_name}
                                    store_total = 0
                                    for category in selected_categories_summary:
                                        if ('수량', category) in pivot_summary.columns:
                                            qty = pivot_summary.loc[store_name, ('수량', category)]
                                            amt = pivot_summary.loc[store_name, ('금액', category)]
                                            row[f'{category}_수량'] = int(qty) if qty == int(qty) else qty
                                            row[f'{category}_금액'] = int(amt)
                                            store_total += amt
                                    row['합계'] = int(store_total)
                                    summary_display.append(row)
                                
                                pd.DataFrame(summary_display).to_excel(writer, sheet_name='매장별정산', index=False)
                            
                            df_export.to_excel(writer, sheet_name='상세내역', index=False)
                        else:
                            # 전체 데이터
                            df_category_summary_all = pd.DataFrame(category_summary)
                            if not df_category_summary_all.empty:
                                pivot_summary = df_category_summary_all.pivot_table(
                                    index='매장명',
                                    columns='카테고리',
                                    values=['수량', '금액'],
                                    aggfunc='sum',
                                    fill_value=0
                                )
                                
                                summary_display = []
                                for store_name in pivot_summary.index:
                                    row = {'매장명': store_name}
                                    store_total = 0
                                    for category in df_prices['카테고리'].unique():
                                        if ('수량', category) in pivot_summary.columns:
                                            qty = pivot_summary.loc[store_name, ('수량', category)]
                                            amt = pivot_summary.loc[store_name, ('금액', category)]
                                            row[f'{category}_수량'] = int(qty) if qty == int(qty) else qty
                                            row[f'{category}_금액'] = int(amt)
                                            store_total += amt
                                    row['합계'] = int(store_total)
                                    summary_display.append(row)
                                
                                pd.DataFrame(summary_display).to_excel(writer, sheet_name='매장별정산', index=False)
                            
                            # 전체 상세 내역
                            export_data_all = []
                            for settlement in settlements:
                                for item in settlement['상세내역']:
                                    export_data_all.append({
                                        '매장명': settlement['매장명'],
                                        '매장코드': settlement['매장코드'],
                                        '날짜': item['날짜'],
                                        '품목명': item['품목명'],
                                        '카테고리': item['카테고리'],
                                        '수량': item['수량'],
                                        '단가': item['단가'],
                                        '금액': item['금액']
                                    })
                            pd.DataFrame(export_data_all).to_excel(writer, sheet_name='상세내역', index=False)
                    
                    excel_data = output.getvalue()
                    
                    # 이메일 메시지 생성
                    msg = MIMEMultipart('mixed')
                    msg['Subject'] = f"[파트너 정산{email_subject_suffix}] {datetime.now().strftime('%Y-%m-%d')} 정산 내역"
                    msg['From'] = sender_email
                    msg['To'] = email_to
                    
                    # HTML 본문 추가
                    html_part = MIMEText(email_body, 'html')
                    msg.attach(html_part)
                    
                    # XLSX 첨부
                    xlsx_attachment = MIMEApplication(excel_data, _subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    xlsx_attachment.add_header('Content-Disposition', 'attachment', filename=f"정산결과_{datetime.now().strftime('%Y%m%d')}.xlsx")
                    msg.attach(xlsx_attachment)
                    
                    # Gmail SMTP 서버로 전송
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                        server.login(sender_email, sender_password)
                        server.send_message(msg)
                    
                    st.success(f"✅ 이메일이 {email_to}로 발송되었습니다!")
                    st.info(f"발신: {sender_email} | 첨부: 정산결과_{datetime.now().strftime('%Y%m%d')}.xlsx")
                
                except Exception as e:
                    st.error(f"❌ 이메일 발송 실패: {str(e)}")
                    st.info("""
                    **문제 해결:**
                    1. Gmail 앱 비밀번호가 올바른지 확인
                    2. 2단계 인증이 활성화되어 있는지 확인
                    3. 앱 비밀번호를 새로 생성해보세요
                    
                    [Gmail 앱 비밀번호 생성하기](https://support.google.com/accounts/answer/185833)
                    """)
            else:
                st.warning("받는 사람 이메일을 입력해주세요.")

else:
    st.info("📤 3개 파일(단가관리, 매장관리, 사용내역)을 모두 업로드해주세요!")
    
    st.markdown("---")
    
    # 샘플 파일 다운로드
    st.subheader("📥 샘플 파일 다운로드")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sample_prices = """품목명,단가,카테고리
비닐봉투(소),50,부자재
비닐봉투(대),100,부자재
박스(소),500,부자재
택배,3000,택배
행낭,1500,행낭"""
        
        st.download_button(
            label="💰 단가관리 샘플",
            data=sample_prices,
            file_name="단가관리_샘플.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        sample_stores = """매장명,매장코드
강남점,GN01
서초점,SC01"""
        
        st.download_button(
            label="🏪 매장관리 샘플",
            data=sample_stores,
            file_name="매장관리_샘플.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        sample_usage = """날짜,매장명,품목명,수량
2024-11-01,강남점,비닐봉투(소),50
2024-11-01,강남점,택배,10"""
        
        st.download_button(
            label="📊 사용내역 샘플",
            data=sample_usage,
            file_name="사용내역_샘플.csv",
            mime="text/csv",
            use_container_width=True
        )

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    💰 파트너 정산 관리 시스템 v3.0 | Made with Streamlit
</div>
""", unsafe_allow_html=True)
