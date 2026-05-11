import requests
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta, timezone
import database as db
import fetcher

scheduler = BackgroundScheduler()

def send_telegram_message(token, chat_id, text):
    """텔레그램 메시지 발송"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"텔레그램 발송 오류: {e}")

def monitor_stocks():
    """등록된 주식을 모니터링하여 조건에 맞으면 알림을 보내고 일별 데이터 저장"""
    # 한국 시간 (UTC+9) 설정
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst)

    # 주말 제외
    if now.weekday() >= 5:
        return
    # 오전 9시 ~ 오후 4시(16:59)까지만 실행
    if not (9 <= now.hour <= 16):
        return

    token = db.get_setting("telegram_token")
    chat_id = db.get_setting("telegram_chat_id")
    portfolio = db.get_portfolio()

    if portfolio.empty:
        return

    msg_lines = ["📊 <b>현재 주식 포트폴리오 현황</b>\n"]
    
    for _, row in portfolio.iterrows():
        symbol = row['symbol']
        name = row['name']
        price_info = fetcher.get_stock_price(symbol)
        
        if price_info:
            change_rate = price_info['change_rate']
            close_price = price_info['close']
            
            # 상승/하락에 따른 기호 추가
            icon = "🔴" if change_rate > 0 else ("🔵" if change_rate < 0 else "⚫")
            msg_lines.append(f"{icon} <b>{name}</b>: {close_price:,}원 ({change_rate}%)")
            
            # 장 마감 시간 (오후 3시 30분 ~ 4시 사이)에 일별 주가 기록 저장
            if now.hour == 15 and now.minute >= 30:
                db.save_daily_history(symbol, now.strftime('%Y-%m-%d'), close_price, change_rate)
        else:
            msg_lines.append(f"⚠️ <b>{name}</b>: 정보 조회 실패")

    final_msg = "\n".join(msg_lines)
    
    if token and chat_id:
        send_telegram_message(token, chat_id, final_msg)

def start_scheduler():
    """스케줄러 시작"""
    if not scheduler.running:
        # 매 15분마다 모니터링 작업 실행
        scheduler.add_job(monitor_stocks, 'interval', minutes=15)
        scheduler.start()
