import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from io import BytesIO

# 페이지 설정
st.set_page_config(
    page_title="파트너 정산 내역 관리 시스템",
    page_icon="🔥",
    layout="wide"
)

# 세션 상태 초기화
if 'df_prices' not in st.session_state:
    st.session_state.df_prices = pd.DataFrame()
if 'df_stores' not in st.session_state:
    st.session_state.df_stores = pd.DataFrame()
if 'df_usage' not in st.session_state:
    st.session_state.df_usage = pd.DataFrame()
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 이메일 설정
DEFAULT_SENDER_EMAIL = "dlwlsgur85@gmail.com"
DEFAULT_SENDER_PASSWORD = "lpmu colo ftnc yvam"

# 타이틀
st.title("🔥 파트너 정산 내역")

# 사이드바 - 로그인
with st.sidebar:
    st.header("🔓 로그인")
    
    if not st.session_state.authenticated:
        password = st.text_input("비밀번호", type="password", key="password_input")
        
        if st.button("로그인", use_container_width=True):
            if password == "dy1234":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ 비밀번호가 틀렸습니다!")
    else:
        st.success("✅ 로그인됨")
        if st.button("로그아웃", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

# 인증되지 않은 경우
if not st.session_state.authenticated:
    st.warning("⚠️ 로그인이 필요합니다.")
    st.stop()

# 메인 화면
st.markdown("### 📊 정산 기간: 2025-11-14")
st.markdown("---")

# 탭 생성
tab1, tab2, tab3, tab4 = st.tabs(["📋 가격 정보", "🏪 매장 정보", "📈 사용 현황", "📧 이메일 발송"])

# ========================================
# 탭 1: 가격 정보
# ========================================
with tab1:
    st.subheader("📋 제품별 가격 정보")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader("엑셀 파일 업로드 (가격 정보)", type=['xlsx', 'xls'], key="price_upload")
        
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                st.session_state.df_prices = df
                st.success("✅ 파일 업로드 완료!")
            except Exception as e:
                st.error(f"❌ 파일 읽기 오류: {e}")
    
    with col2:
        if st.button("➕ 새 행 추가", key="add_price_row"):
            new_row = pd.DataFrame([{
                '제품명': '',
                '수량': 0,
                '금액': 0
            }])
            st.session_state.df_prices = pd.concat([st.session_state.df_prices, new_row], ignore_index=True)
    
    if not st.session_state.df_prices.empty:
        edited_df = st.data_editor(
            st.session_state.df_prices,
            use_container_width=True,
            num_rows="dynamic",
            key="price_editor"
        )
        st.session_state.df_prices = edited_df
        
        # 합계 표시
        if '금액' in edited_df.columns:
            total = edited_df['금액'].sum()
            st.metric("💰 총 금액", f"{total:,}원")

# ========================================
# 탭 2: 매장 정보
# ========================================
with tab2:
    st.subheader("🏪 매장별 정보")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader("엑셀 파일 업로드 (매장 정보)", type=['xlsx', 'xls'], key="store_upload")
        
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                st.session_state.df_stores = df
                st.success("✅ 파일 업로드 완료!")
            except Exception as e:
                st.error(f"❌ 파일 읽기 오류: {e}")
    
    with col2:
        if st.button("➕ 새 행 추가", key="add_store_row"):
            new_row = pd.DataFrame([{
                '매장명': '',
                '쇼핑백 수량': 0,
                '쇼핑백 금액': 0,
                '플라백 수량': 0,
                '플라백 금액': 0,
                '테이프 수량': 0,
                '테이프 금액': 0,
                '박스 수량': 0,
                '박스 금액': 0,
                '행낭 수량': 0,
                '행낭 금액': 0,
                '택배 수량': 0,
                '택배 금액': 0,
                '합계': 0
            }])
            st.session_state.df_stores = pd.concat([st.session_state.df_stores, new_row], ignore_index=True)
    
    if not st.session_state.df_stores.empty:
        edited_df = st.data_editor(
            st.session_state.df_stores,
            use_container_width=True,
            num_rows="dynamic",
            key="store_editor"
        )
        st.session_state.df_stores = edited_df
        
        # 합계 표시
        if '합계' in edited_df.columns:
            total = edited_df['합계'].sum()
            st.metric("💰 전체 매장 합계", f"{total:,}원")

# ========================================
# 탭 3: 사용 현황
# ========================================
with tab3:
    st.subheader("📈 자재 사용 현황")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader("엑셀 파일 업로드 (사용 현황)", type=['xlsx', 'xls'], key="usage_upload")
        
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                st.session_state.df_usage = df
                st.success("✅ 파일 업로드 완료!")
            except Exception as e:
                st.error(f"❌ 파일 읽기 오류: {e}")
    
    with col2:
        if st.button("➕ 새 행 추가", key="add_usage_row"):
            new_row = pd.DataFrame([{
                '항목': '',
                '사용량': 0,
                '단가': 0,
                '금액': 0
            }])
            st.session_state.df_usage = pd.concat([st.session_state.df_usage, new_row], ignore_index=True)
    
    if not st.session_state.df_usage.empty:
        edited_df = st.data_editor(
            st.session_state.df_usage,
            use_container_width=True,
            num_rows="dynamic",
            key="usage_editor"
        )
        st.session_state.df_usage = edited_df
        
        # 합계 표시
        if '금액' in edited_df.columns:
            total = edited_df['금액'].sum()
            st.metric("💰 총 금액", f"{total:,}원")

# ========================================
# 탭 4: 이메일 발송
# ========================================
with tab4:
    st.subheader("📧 이메일 발송")
    
    # 이메일 설정
    col1, col2 = st.columns(2)
    
    with col1:
        sender_email = st.text_input("발신자 이메일", value=DEFAULT_SENDER_EMAIL)
        sender_password = st.text_input("앱 비밀번호", value=DEFAULT_SENDER_PASSWORD, type="password")
    
    with col2:
        recipient_email = st.text_input("수신자 이메일", value="jinhyuk.lee@dae-yeon.co.kr")
        email_subject = st.text_input("이메일 제목", value="[파트너 정산] 2025-11-14 정산 내역")
    
    st.markdown("---")
    
    # 이메일 미리보기
    with st.expander("📋 이메일 미리보기", expanded=True):
        st.markdown("### 파트너 정산 내역")
        st.markdown(f"**정산 기간:** 2025-11-14")
        
        if not st.session_state.df_stores.empty:
            st.markdown("### 매장별 정산 내역")
            
            # 전체 합계 계산
            total_amount = st.session_state.df_stores['합계'].sum() if '합계' in st.session_state.df_stores.columns else 0
            st.metric("전체 정산 금액", f"{total_amount:,}원")
            
            st.dataframe(st.session_state.df_stores, use_container_width=True)
    
    # HTML 이메일 생성 함수
    def create_html_email(df_stores):
        """테두리가 명확한 HTML 테이블 생성"""
        
        # 전체 합계
        total_amount = df_stores['합계'].sum() if '합계' in df_stores.columns else 0
        
        html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: 'Malgun Gothic', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .header {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-left: 4px solid #ff6b6b;
                }}
                .content {{
                    padding: 20px;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                    font-size: 13px;
                }}
                th {{
                    background-color: #495057;
                    color: white;
                    padding: 12px 8px;
                    text-align: center;
                    border: 1px solid #dee2e6;
                    font-weight: bold;
                }}
                td {{
                    padding: 10px 8px;
                    text-align: center;
                    border: 1px solid #dee2e6;
                }}
                tr:nth-child(even) {{
                    background-color: #f8f9fa;
                }}
                tr:hover {{
                    background-color: #e9ecef;
                }}
                .total-row {{
                    background-color: #fff3cd !important;
                    font-weight: bold;
                }}
                .footer {{
                    margin-top: 30px;
                    padding: 15px;
                    background-color: #f8f9fa;
                    border-top: 2px solid #dee2e6;
                    font-size: 12px;
                    color: #6c757d;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🔥 파트너 정산 내역</h2>
                <p><strong>정산 기간:</strong> 2025-11-14</p>
                <p><strong>전체 정산 금액:</strong> {total_amount:,}원</p>
            </div>
            
            <div class="content">
                <h3>매장별 정산 내역</h3>
                
                <table>
                    <thead>
                        <tr>
                            <th rowspan="2">매장명</th>
                            <th colspan="2">쇼핑백</th>
                            <th colspan="2">플라백</th>
                            <th colspan="2">테이프</th>
                            <th colspan="2">박스</th>
                            <th colspan="2">행낭</th>
                            <th colspan="2">택배</th>
                            <th rowspan="2">합계</th>
                        </tr>
                        <tr>
                            <th>수량</th>
                            <th>금액</th>
                            <th>수량</th>
                            <th>금액</th>
                            <th>수량</th>
                            <th>금액</th>
                            <th>수량</th>
                            <th>금액</th>
                            <th>수량</th>
                            <th>금액</th>
                            <th>수량</th>
                            <th>금액</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # 데이터 행 추가
        for _, row in df_stores.iterrows():
            html += "<tr>"
            html += f"<td>{row.get('매장명', '')}</td>"
            html += f"<td>{row.get('쇼핑백 수량', 0)}</td>"
            html += f"<td>{row.get('쇼핑백 금액', 0):,}원</td>"
            html += f"<td>{row.get('플라백 수량', 0)}</td>"
            html += f"<td>{row.get('플라백 금액', 0):,}원</td>"
            html += f"<td>{row.get('테이프 수량', 0)}</td>"
            html += f"<td>{row.get('테이프 금액', 0):,}원</td>"
            html += f"<td>{row.get('박스 수량', 0)}</td>"
            html += f"<td>{row.get('박스 금액', 0):,}원</td>"
            html += f"<td>{row.get('행낭 수량', 0)}</td>"
            html += f"<td>{row.get('행낭 금액', 0):,}원</td>"
            html += f"<td>{row.get('택배 수량', 0)}</td>"
            html += f"<td>{row.get('택배 금액', 0):,}원</td>"
            html += f"<td><strong>{row.get('합계', 0):,}원</strong></td>"
            html += "</tr>"
        
        html += """
                    </tbody>
                </table>
            </div>
            
            <div class="footer">
                <p>※ 상세 내역은 첨부된 XLSX 파일을 확인해주세요.</p>
                <p>문의사항이 있으시면 연락 주시기 바랍니다.</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    # 이메일 발송 버튼
    if st.button("📤 이메일 발송", type="primary", use_container_width=True):
        if st.session_state.df_stores.empty:
            st.error("❌ 매장 정보가 없습니다!")
        else:
            try:
                # HTML 이메일 생성
                html_content = create_html_email(st.session_state.df_stores)
                
                # 이메일 메시지 생성
                msg = MIMEMultipart('alternative')
                msg['Subject'] = email_subject
                msg['From'] = sender_email
                msg['To'] = recipient_email
                
                # HTML 첨부
                html_part = MIMEText(html_content, 'html', 'utf-8')
                msg.attach(html_part)
                
                # SMTP 서버 연결 및 발송
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(sender_email, sender_password)
                    server.send_message(msg)
                
                st.success("✅ 이메일이 성공적으로 발송되었습니다!")
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ 이메일 발송 실패: {e}")

# ========================================
# 푸터
# ========================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #6c757d; font-size: 12px;'>
        <p>파트너 정산 내역 관리 시스템 v1.0 | © 2025</p>
    </div>
    """,
    unsafe_allow_html=True
)
