from sqlalchemy import create_engine, text
import pandas as pd
import os
import streamlit as st

def is_supabase():
    # Streamlit secrets에 연결 정보가 있는지 확인
    if 'connections' in st.secrets and 'supabase' in st.secrets.connections:
        return True
    if 'SUPABASE_URL' in st.secrets:
        return True
    return False

def get_supabase_client():
    from st_supabase_connection import SupabaseConnection
    return st.connection("supabase", type=SupabaseConnection)

def get_engine():
    """SQLite 전용 엔진 생성 (Supabase 사용 시 호출 안 함)"""
    os.makedirs('data', exist_ok=True)
    return create_engine('sqlite:///data/portfolio.db')

def init_db():
    if is_supabase():
        # Supabase REST API는 DDL(CREATE TABLE)을 지원하지 않으므로 테이블은 대시보드에서 생성되어 있어야 함
        pass
    else:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS portfolio (
                    symbol VARCHAR(20) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''))
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS daily_history (
                    symbol VARCHAR(20) NOT NULL,
                    date VARCHAR(20) NOT NULL,
                    close_price INTEGER,
                    change_rate REAL,
                    PRIMARY KEY (symbol, date)
                )
            '''))
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS settings (
                    key VARCHAR(100) PRIMARY KEY,
                    value TEXT
                )
            '''))
            conn.commit()

def get_portfolio():
    if is_supabase():
        try:
            client = get_supabase_client()
            response = client.table("portfolio").select("*").execute()
            return pd.DataFrame(response.data)
        except Exception as e:
            print(f"Supabase get_portfolio error: {e}")
            return pd.DataFrame()
    else:
        engine = get_engine()
        try:
            df = pd.read_sql_query('SELECT * FROM portfolio', engine)
            return df
        except Exception:
            return pd.DataFrame()

def add_stock(symbol, name):
    success = False
    if is_supabase():
        try:
            st.text("Supabase add_stock")  
            client = get_supabase_client()
            st.text("Supabase add_stock2")  
            client.table("portfolio").insert({"symbol": symbol, "name": name}).execute()
            st.text("Supabase add_stock3")  
            success = True
        except Exception as e:
            print(f"Supabase add_stock error: {e}")
            success = False
    else:
        engine = get_engine()
        with engine.connect() as conn:
            try:
                conn.execute(text('INSERT INTO portfolio (symbol, name) VALUES (:s, :n)'), {"s": symbol, "n": name})
                conn.commit()
                success = True
            except Exception as e:
                print(f"종목 추가 에러: {e}")
                success = False
    return success

def delete_stock(symbol):
    if is_supabase():
        try:
            client = get_supabase_client()
            client.table("portfolio").delete().eq("symbol", symbol).execute()
        except Exception as e:
            print(f"Supabase delete_stock error: {e}")
    else:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text('DELETE FROM portfolio WHERE symbol = :s'), {"s": symbol})
            conn.commit()

def save_daily_history(symbol, date, close_price, change_rate):
    if is_supabase():
        try:
            client = get_supabase_client()
            client.table("daily_history").upsert({
                "symbol": symbol,
                "date": date,
                "close_price": close_price,
                "change_rate": change_rate
            }).execute()
        except Exception as e:
            print(f"Supabase save_daily_history error: {e}")
    else:
        engine = get_engine()
        with engine.connect() as conn:
            try:
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
    if is_supabase():
        try:
            client = get_supabase_client()
            response = client.table("settings").select("value").eq("key", key).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]["value"]
            return None
        except Exception as e:
            print(f"Supabase get_setting error: {e}")
            return None
    else:
        engine = get_engine()
        with engine.connect() as conn:
            try:
                row = conn.execute(text('SELECT value FROM settings WHERE key = :k'), {"k": key}).fetchone()
                return row[0] if row else None
            except Exception:
                return None

def set_setting(key, value):
    if is_supabase():
        try:
            client = get_supabase_client()
            client.table("settings").upsert({"key": key, "value": value}).execute()
        except Exception as e:
            print(f"Supabase set_setting error: {e}")
    else:
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
