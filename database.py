from sqlalchemy import create_engine, text
import pandas as pd
import os
import streamlit as st

def get_engine():
    """Streamlit secrets에 DB_URL이 있으면 PostgreSQL, 없으면 로컬 SQLite 사용"""
    try:
        if 'DB_URL' in st.secrets:
            return create_engine(st.secrets['DB_URL'])
    except Exception:
        pass
        
    os.makedirs('data', exist_ok=True)
    return create_engine('sqlite:///data/portfolio.db')

def init_db():
    engine = get_engine()
    with engine.connect() as conn:
        # 종목 테이블 (symbol을 PK로 사용)
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS portfolio (
                symbol VARCHAR(20) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''))
        # 일별 주가 기록 테이블 (symbol과 date 복합키)
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS daily_history (
                symbol VARCHAR(20) NOT NULL,
                date VARCHAR(20) NOT NULL,
                close_price INTEGER,
                change_rate REAL,
                PRIMARY KEY (symbol, date)
            )
        '''))
        # 설정 테이블
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS settings (
                key VARCHAR(100) PRIMARY KEY,
                value TEXT
            )
        '''))
        conn.commit()

def get_portfolio():
    engine = get_engine()
    try:
        df = pd.read_sql_query('SELECT * FROM portfolio', engine)
        return df
    except Exception:
        return pd.DataFrame()

def add_stock(symbol, name):
    engine = get_engine()
    success = False
    with engine.connect() as conn:
        try:
            # PostgreSQL과 SQLite 호환되도록 단순 INSERT 사용 (기존에 있으면 예외 발생)
            conn.execute(text('INSERT INTO portfolio (symbol, name) VALUES (:s, :n)'), {"s": symbol, "n": name})
            conn.commit()
            success = True
        except Exception as e:
            print(f"종목 추가 에러: {e}")
            success = False
    return success

def delete_stock(symbol):
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text('DELETE FROM portfolio WHERE symbol = :s'), {"s": symbol})
        conn.commit()

def save_daily_history(symbol, date, close_price, change_rate):
    engine = get_engine()
    with engine.connect() as conn:
        try:
            # 기존 레코드 존재 확인 (Upsert 호환성을 위해)
            result = conn.execute(text('SELECT 1 FROM daily_history WHERE symbol=:s AND date=:d'), {"s": symbol, "d": date}).fetchone()
            if result:
                conn.execute(text('UPDATE daily_history SET close_price=:p, change_rate=:r WHERE symbol=:s AND date=:d'), 
                             {"s": symbol, "d": date, "p": close_price, "r": change_rate})
            else:
                conn.execute(text('INSERT INTO daily_history (symbol, date, close_price, change_rate) VALUES (:s, :d, :p, :r)'), 
                             {"s": symbol, "d": date, "p": close_price, "r": change_rate})
            conn.commit()
        except Exception as e:
            print(f"History save error: {e}")

def get_setting(key):
    engine = get_engine()
    with engine.connect() as conn:
        try:
            row = conn.execute(text('SELECT value FROM settings WHERE key = :k'), {"k": key}).fetchone()
            return row[0] if row else None
        except Exception:
            return None

def set_setting(key, value):
    engine = get_engine()
    with engine.connect() as conn:
        try:
            result = conn.execute(text('SELECT 1 FROM settings WHERE key=:k'), {"k": key}).fetchone()
            if result:
                conn.execute(text('UPDATE settings SET value=:v WHERE key=:k'), {"k": key, "v": value})
            else:
                conn.execute(text('INSERT INTO settings (key, value) VALUES (:k, :v)'), {"k": key, "v": value})
            conn.commit()
        except Exception as e:
            print(f"Setting save error: {e}")
