import streamlit as st
import pandas as pd
import database as db
import fetcher
import scheduler

# 페이지 설정
st.set_page_config(page_title="주식 모니터링 대시보드", page_icon="📈", layout="wide")

@st.cache_resource
def init_system():
    db.init_db()
    scheduler.start_scheduler()
    return True

init_system()

st.title("📈 주식 모니터링 대시보드")
st.markdown("매일 등록한 주식의 주가 정보 및 뉴스를 모아보고, 5% 이상 하락 시 텔레그램 알림을 받으세요.")

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 시스템 설정")
    with st.expander("텔레그램 알림 설정"):
        token = st.text_input("Bot Token", value=db.get_setting("telegram_token") or "", type="password")
        chat_id = st.text_input("Chat ID", value=db.get_setting("telegram_chat_id") or "")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("설정 저장", use_container_width=True):
                db.set_setting("telegram_token", token)
                db.set_setting("telegram_chat_id", chat_id)
                st.success("설정이 저장되었습니다.")
        with col2:
            if st.button("전송 테스트", use_container_width=True):
                if token and chat_id:
                    scheduler.send_telegram_message(token, chat_id, "✅ <b>주식 모니터링 알림 테스트</b>가 성공적으로 전송되었습니다!")
                    st.success("테스트 메시지를 전송했습니다. 텔레그램을 확인해주세요.")
                else:
                    st.error("토큰과 Chat ID를 모두 입력해주세요.")
            
    st.header("📋 포트폴리오 관리")
    with st.form("add_stock_form"):
        new_name = st.text_input("추가할 종목명 (예: 삼성전자)")
        submit = st.form_submit_button("종목 추가")
        if submit and new_name:
            new_name = new_name.strip()
            with st.spinner("종목 코드 검색 중..."):
                symbol = fetcher.get_stock_code_by_name(new_name)
                st.text(symbol) 
            if symbol:
                if db.add_stock(symbol, new_name):
                    st.success(f"'{new_name}' ({symbol}) 추가 완료!")
                    st.rerun()
                else:
                    st.error("이미 존재하는 종목이거나 오류가 발생했습니다.")
            else:
                st.error("해당 종목을 찾을 수 없습니다. 정확한 종목명을 입력해주세요.")

    portfolio_df = db.get_portfolio()
    if not portfolio_df.empty:
        st.subheader("등록된 종목 삭제")
        del_symbol = st.selectbox("삭제할 종목 선택", portfolio_df['symbol'] + " (" + portfolio_df['name'] + ")")
        if st.button("종목 삭제"):
            symbol_to_del = del_symbol.split(" ")[0]
            db.delete_stock(symbol_to_del)
            st.success("삭제 완료!")
            st.rerun()

# 메인 화면
st.header("📊 현재 포트폴리오 현황")

if portfolio_df.empty:
    st.info("사이드바에서 모니터링할 종목을 추가해주세요.")
else:
    # 종목 현황 표 생성
    summary_data = []
    with st.spinner("주가 정보를 불러오는 중입니다..."):
        for _, row in portfolio_df.iterrows():
            symbol = row['symbol']
            name = row['name']
            price_info = fetcher.get_stock_price(symbol)
            if price_info:
                summary_data.append({
                    "종목명": name,
                    "종목코드": symbol,
                    "현재가(원)": f"{price_info['close']:,}",
                    "등락률(%)": price_info['change_rate']
                })
            else:
                summary_data.append({
                    "종목명": name,
                    "종목코드": symbol,
                    "현재가(원)": "조회 실패",
                    "등락률(%)": "-"
                })
                
    summary_df = pd.DataFrame(summary_data)
    
    if not summary_df.empty:
        st.markdown("💡 **목록에서 종목을 클릭하시면 아래에 상세 정보(차트 및 뉴스)가 표시됩니다.**")
        
        # 등락률 색상 지정을 위한 스타일 함수
        def color_change_rate(val):
            try:
                if val > 0:
                    return 'color: #ff4b4b' # 빨간색
                elif val < 0:
                    return 'color: #31333f' # 기본색 (또는 파란색 #0068c9)
            except:
                pass
            return ''

        # 등락률 파란색/빨간색 적용 및 포맷팅
        def style_positive_negative(val):
            if isinstance(val, (int, float)):
                color = 'red' if val > 0 else 'blue' if val < 0 else 'black'
                return f'color: {color}'
            return ''

        styled_df = summary_df.style.map(style_positive_negative, subset=['등락률(%)'])

        event = st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )

    # 종목 상세 정보
    st.header("🔍 종목 상세 정보 (차트 및 뉴스)")
    
    selected_symbol = None
    selected_name = None

    if not summary_df.empty:
        if event.selection and event.selection.rows:
            row_idx = event.selection.rows[0]
            selected_symbol = summary_df.iloc[row_idx]['종목코드']
            selected_name = summary_df.iloc[row_idx]['종목명']
        else:
            # 기본적으로 첫 번째 종목 선택
            selected_symbol = summary_df.iloc[0]['종목코드']
            selected_name = summary_df.iloc[0]['종목명']
            
    if selected_symbol and selected_name:
        
        # 1. 6개월 차트
        st.subheader("📈 최근 6개월 주가 차트")
        with st.spinner("차트 데이터를 불러오는 중..."):
            chart_df = fetcher.get_stock_history(selected_symbol, months=6)
            if chart_df is not None and not chart_df.empty:
                # Streamlit의 내장 line_chart 활용 (Close(종가) 기준)
                st.line_chart(chart_df['Close'])
            else:
                st.write("차트 데이터를 불러올 수 없습니다.")
                
        # 2. 관련 주요 뉴스
        st.subheader("📰 관련 주요 뉴스")
        with st.spinner(f"'{selected_name}' 뉴스를 불러오는 중..."):
            news = fetcher.get_stock_news(selected_symbol)
            if news:
                for n in news:
                    st.markdown(f"- **[{n['title']}]({n['link']})** ({n['date']})")
            else:
                st.write("관련 뉴스를 찾을 수 없습니다.")
