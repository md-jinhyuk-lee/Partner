import streamlit as st
import pandas as pd
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="파트너 정산 관리",
    page_icon="💰",
    layout="wide"
)

# 제목
st.title("💰 파트너 정산 관리 시스템")
st.markdown("### 부자재 · 택배 · 행낭 사용 비용 자동 정산")

# 사이드바 - 패스워드
with st.sidebar:
    st.header("🔐 로그인")
    password = st.text_input("패스워드", type="password", value="")
    
    if password != "dy1234":
        st.error("❌ 패스워드를 입력하세요")
        st.stop()
    else:
        st.success("✅ 인증 완료")
    
    st.divider()
    
    st.markdown("""
    ### 📋 사용 방법
    
    1. **단가관리** 파일 업로드
    2. **매장관리** 파일 업로드
    3. **사용내역** 파일 업로드
    
    → 자동으로 정산 계산!
    """)
    
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
    
    **사용내역.csv (옵션 1: 매장코드)**
    ```
    날짜,매장코드,품목명,수량
    2024-11-01,GN01,비닐봉투(소),50
    ```
    
    **사용내역.csv (옵션 2: 매장명)**
    ```
    날짜,매장명,품목명,수량
    2024-11-01,강남점,비닐봉투(소),50
    ```
    
    💡 **매장코드 또는 매장명 중 선택!**
    """)

# 메인 영역
st.header("📤 파일 업로드")

# 3개 열로 나누기
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
        try:
            # UTF-8 시도
            df_prices = pd.read_csv(price_file, encoding='utf-8')
        except UnicodeDecodeError:
            # CP949(EUC-KR) 시도
            price_file.seek(0)  # 파일 포인터 초기화
            try:
                df_prices = pd.read_csv(price_file, encoding='cp949')
            except:
                price_file.seek(0)
                df_prices = pd.read_csv(price_file, encoding='euc-kr')
        
        # 컬럼명 공백 제거
        df_prices.columns = df_prices.columns.str.strip()
        
        # 필수 컬럼 체크
        required_cols = ['품목명', '단가', '카테고리']
        missing_cols = [col for col in required_cols if col not in df_prices.columns]
        
        if missing_cols:
            st.error(f"❌ 단가관리 파일에 필수 컬럼이 없습니다: {', '.join(missing_cols)}")
            st.info(f"현재 컬럼: {', '.join(df_prices.columns.tolist())}")
            st.warning("필요한 컬럼: 품목명, 단가, 카테고리")
        else:
            st.success(f"✅ {len(df_prices)}개 품목 로드")
            with st.expander("데이터 미리보기"):
                st.dataframe(df_prices, hide_index=True)

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
        try:
            df_stores = pd.read_csv(store_file, encoding='utf-8')
        except UnicodeDecodeError:
            store_file.seek(0)
            try:
                df_stores = pd.read_csv(store_file, encoding='cp949')
            except:
                store_file.seek(0)
                df_stores = pd.read_csv(store_file, encoding='euc-kr')
        
        # 컬럼명 공백 제거
        df_stores.columns = df_stores.columns.str.strip()
        
        # 필수 컬럼 체크
        required_cols = ['매장명', '매장코드']
        missing_cols = [col for col in required_cols if col not in df_stores.columns]
        
        if missing_cols:
            st.error(f"❌ 매장관리 파일에 필수 컬럼이 없습니다: {', '.join(missing_cols)}")
            st.info(f"현재 컬럼: {', '.join(df_stores.columns.tolist())}")
            st.warning("필요한 컬럼: 매장명, 매장코드")
        else:
            st.success(f"✅ {len(df_stores)}개 매장 로드")
            with st.expander("데이터 미리보기"):
                st.dataframe(df_stores, hide_index=True)

# 사용내역 업로드
with col3:
    st.subheader("📊 사용내역")
    usage_file = st.file_uploader(
        "사용내역 CSV 파일",
        type=['csv'],
        key="usage_file",
        help="날짜, 매장코드, 품목명, 수량"
    )
    
    if usage_file:
        try:
            df_usage = pd.read_csv(usage_file, encoding='utf-8')
        except UnicodeDecodeError:
            usage_file.seek(0)
            try:
                df_usage = pd.read_csv(usage_file, encoding='cp949')
            except:
                usage_file.seek(0)
                df_usage = pd.read_csv(usage_file, encoding='euc-kr')
        
        # 컬럼명 공백 제거
        df_usage.columns = df_usage.columns.str.strip()
        
        # 필수 컬럼 체크 (매장코드 또는 매장명 중 하나만 있으면 됨)
        has_store_code = '매장코드' in df_usage.columns
        has_store_name = '매장명' in df_usage.columns
        
        if not (has_store_code or has_store_name):
            st.error("❌ 사용내역 파일에 '매장코드' 또는 '매장명' 컬럼이 필요합니다.")
            st.info(f"현재 컬럼: {', '.join(df_usage.columns.tolist())}")
            st.warning("필요한 컬럼: 날짜, (매장코드 또는 매장명), 품목명, 수량")
        elif '날짜' not in df_usage.columns or '품목명' not in df_usage.columns or '수량' not in df_usage.columns:
            missing = []
            if '날짜' not in df_usage.columns: missing.append('날짜')
            if '품목명' not in df_usage.columns: missing.append('품목명')
            if '수량' not in df_usage.columns: missing.append('수량')
            st.error(f"❌ 사용내역 파일에 필수 컬럼이 없습니다: {', '.join(missing)}")
            st.info(f"현재 컬럼: {', '.join(df_usage.columns.tolist())}")
        else:
            store_col_type = "매장명" if has_store_name else "매장코드"
            st.success(f"✅ {len(df_usage)}건 로드 ({store_col_type} 사용)")
            with st.expander("데이터 미리보기"):
                st.dataframe(df_usage.head(10), hide_index=True)

st.divider()

# 정산 계산
if price_file and store_file and usage_file:
    st.header("📊 정산 결과")
    
    # 컬럼 존재 여부 확인
    price_cols_ok = all(col in df_prices.columns for col in ['품목명', '단가', '카테고리'])
    store_cols_ok = all(col in df_stores.columns for col in ['매장명', '매장코드'])
    usage_has_store = '매장코드' in df_usage.columns or '매장명' in df_usage.columns
    usage_cols_ok = all(col in df_usage.columns for col in ['날짜', '품목명', '수량']) and usage_has_store
    
    if not (price_cols_ok and store_cols_ok and usage_cols_ok):
        st.error("⚠️ 일부 파일의 컬럼명이 올바르지 않습니다. 위의 에러 메시지를 확인해주세요.")
        st.stop()
    
    # 요약 통계
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("등록 품목", f"{len(df_prices)}개")
    
    with col2:
        st.metric("등록 매장", f"{len(df_stores)}개")
    
    with col3:
        st.metric("사용 건수", f"{len(df_usage)}건")
    
    # 정산 계산
    settlements = []
    total_amount = 0
    
    # 사용내역이 매장코드를 사용하는지 매장명을 사용하는지 확인
    use_store_code = '매장코드' in df_usage.columns
    
    for _, store in df_stores.iterrows():
        store_code = store['매장코드']
        store_name = store['매장명']
        
        # 해당 매장의 사용내역 필터링
        if use_store_code:
            # 매장코드로 필터링
            store_usage = df_usage[df_usage['매장코드'] == store_code]
        else:
            # 매장명으로 필터링
            store_usage = df_usage[df_usage['매장명'] == store_name]
        
        if not store_usage.empty:
            store_total = 0
            items_detail = []
            
            for _, usage in store_usage.iterrows():
                item_name = usage['품목명']
                quantity = usage['수량']
                
                # 단가 찾기
                price_info = df_prices[df_prices['품목명'] == item_name]
                
                if not price_info.empty:
                    unit_price = price_info.iloc[0]['단가']
                    subtotal = unit_price * quantity
                    store_total += subtotal
                    
                    items_detail.append({
                        '날짜': usage['날짜'],
                        '품목명': item_name,
                        '수량': quantity,
                        '단가': unit_price,
                        '소계': subtotal
                    })
                else:
                    st.warning(f"⚠️ '{item_name}' 품목의 단가가 등록되지 않았습니다.")
            
            if items_detail:
                settlements.append({
                    '매장명': store_name,
                    '매장코드': store_code,
                    '상세내역': items_detail,
                    '합계': store_total
                })
                total_amount += store_total
    
    # 전체 정산 금액
    with col4:
        st.metric("전체 정산 금액", f"{total_amount:,}원")
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 30px; border-radius: 15px; margin: 30px 0;'>
        <h2 style='color: white; margin: 0;'>💵 전체 정산 금액</h2>
        <h1 style='color: white; margin: 10px 0 0 0; font-size: 52px;'>
            {total_amount:,}원
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # 매장별 정산 상세
    st.subheader("🏪 매장별 정산 내역")
    
    for settlement in settlements:
        with st.expander(
            f"**{settlement['매장명']}** ({settlement['매장코드']}) - **{settlement['합계']:,}원**",
            expanded=True
        ):
            df_detail = pd.DataFrame(settlement['상세내역'])
            
            # 포맷팅
            df_detail['단가'] = df_detail['단가'].apply(lambda x: f"{x:,}원")
            df_detail['소계'] = df_detail['소계'].apply(lambda x: f"{x:,}원")
            
            st.dataframe(
                df_detail,
                use_container_width=True,
                hide_index=True
            )
            
            # 매장 합계
            st.markdown(f"""
            <div style='background-color: #f0f0f0; padding: 15px; border-radius: 8px; margin-top: 10px;'>
                <h3 style='margin: 0; text-align: right;'>
                    매장 합계: <span style='color: #667eea;'>{settlement['합계']:,}원</span>
                </h3>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # 다운로드 버튼
    st.subheader("💾 결과 다운로드")
    
    # 정산 결과를 데이터프레임으로 변환
    export_data = []
    for settlement in settlements:
        for item in settlement['상세내역']:
            export_data.append({
                '매장명': settlement['매장명'],
                '매장코드': settlement['매장코드'],
                '날짜': item['날짜'],
                '품목명': item['품목명'],
                '수량': item['수량'],
                '단가': item['단가'],
                '소계': item['소계']
            })
    
    df_export = pd.DataFrame(export_data)
    
    # 합계 행 추가
    total_row = pd.DataFrame([{
        '매장명': '전체 합계',
        '매장코드': '',
        '날짜': '',
        '품목명': '',
        '수량': '',
        '단가': '',
        '소계': total_amount
    }])
    
    df_export = pd.concat([df_export, total_row], ignore_index=True)
    
    # CSV 다운로드
    csv = df_export.to_csv(index=False, encoding='utf-8-sig')
    
    st.download_button(
        label="📥 정산 결과 다운로드 (CSV)",
        data=csv,
        file_name=f"정산결과_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    # 상세 내역 테이블
    st.subheader("📋 전체 상세 내역")
    st.dataframe(df_export, use_container_width=True, hide_index=True)

else:
    st.info("📤 위에서 3개 파일(단가관리, 매장관리, 사용내역)을 모두 업로드해주세요!")
    
    st.markdown("---")
    
    # 샘플 파일 다운로드
    st.subheader("📥 샘플 파일 다운로드")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sample_prices = """품목명,단가,카테고리
비닐봉투(소),50,부자재
비닐봉투(대),100,부자재
박스(소),500,부자재
박스(중),800,부자재
박스(대),1200,부자재
테이프,300,부자재
에어캡,200,부자재
택배,3000,택배
택배(착불),3500,택배
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
서초점,SC01
역삼점,YS01
논현점,NH01
신사점,SS01"""
        
        st.download_button(
            label="🏪 매장관리 샘플",
            data=sample_stores,
            file_name="매장관리_샘플.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        sample_usage = """날짜,매장코드,품목명,수량
2024-11-01,GN01,비닐봉투(소),50
2024-11-01,GN01,비닐봉투(대),30
2024-11-01,GN01,택배,10
2024-11-01,GN01,행낭,5
2024-11-02,SC01,비닐봉투(소),40
2024-11-02,SC01,박스(소),15
2024-11-02,SC01,택배,8
2024-11-03,YS01,비닐봉투(대),25
2024-11-03,YS01,테이프,10
2024-11-03,YS01,행낭,3"""
        
        st.download_button(
            label="📊 사용내역 샘플 (매장코드)",
            data=sample_usage,
            file_name="사용내역_샘플_매장코드.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        sample_usage_name = """날짜,매장명,품목명,수량
2024-11-01,강남점,비닐봉투(소),50
2024-11-01,강남점,비닐봉투(대),30
2024-11-01,강남점,택배,10
2024-11-01,강남점,행낭,5
2024-11-02,서초점,비닐봉투(소),40
2024-11-02,서초점,박스(소),15
2024-11-02,서초점,택배,8
2024-11-03,역삼점,비닐봉투(대),25
2024-11-03,역삼점,테이프,10
2024-11-03,역삼점,행낭,3"""
        
        st.download_button(
            label="📊 사용내역 샘플 (매장명)",
            data=sample_usage_name,
            file_name="사용내역_샘플_매장명.csv",
            mime="text/csv",
            use_container_width=True
        )

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    💰 파트너 정산 관리 시스템 v2.0 | Made with Streamlit
</div>
""", unsafe_allow_html=True)
