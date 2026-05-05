import FinanceDataReader as fdr
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

def get_stock_price(symbol):
    """지정된 종목의 최신 주가 정보 조회"""
    # 주말이나 휴일에는 오늘 데이터가 없으므로 최근 7일치 데이터를 가져와서 가장 최근 영업일 데이터를 사용
    start_date = (datetime.today() - pd.Timedelta(days=7)).strftime('%Y-%m-%d')
    try:
        df = fdr.DataReader(symbol, start_date)
        if not df.empty:
            latest = df.iloc[-1]
            change_rate = 0.0
            if 'Change' in latest:
                change_rate = round(latest['Change'] * 100, 2)
            return {
                'close': int(latest['Close']),
                'change_rate': change_rate
            }
    except Exception as e:
        print(f"주가 조회 오류 ({symbol}): {e}")
    return None

def get_stock_history(symbol, months=6):
    """지정된 종목의 최근 N개월 주가 역사 데이터 조회"""
    start_date = (datetime.today() - pd.DateOffset(months=months)).strftime('%Y-%m-%d')
    try:
        df = fdr.DataReader(symbol, start_date)
        if not df.empty:
            return df
    except Exception as e:
        print(f"주가 역사 데이터 조회 오류 ({symbol}): {e}")
    return None

def get_stock_code_by_name(name):
    """한글 종목명으로 종목 코드(Symbol)를 찾습니다. (일반 주식 및 ETF 지원)"""
    try:
        # 일반 상장 종목 검색
        df_krx = fdr.StockListing('KRX')
        result = df_krx[df_krx['Name'] == name]
        if not result.empty:
            return result.iloc[0]['Code']
            
        # ETF 검색 추가
        df_etf = fdr.StockListing('ETF/KR')
        result_etf = df_etf[df_etf['Name'] == name]
        if not result_etf.empty:
            return result_etf.iloc[0]['Symbol']
    except Exception as e:
        print(f"종목 코드 검색 오류: {e}")
    return None

def get_stock_news(symbol):
    """네이버 금융에서 종목의 최신 뉴스 5개 조회"""
    url = f"https://finance.naver.com/item/news_news.naver?code={symbol}&page=1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': f'https://finance.naver.com/item/news.naver?code={symbol}'
    }
    try:
        res = requests.get(url, headers=headers)
        res.encoding = 'euc-kr'
        soup = BeautifulSoup(res.text, 'html.parser')
        news_list = []
        for tr in soup.select('.type5 tbody tr'):
            title_td = tr.select_one('.title')
            if title_td and title_td.a:
                title = title_td.a.text.strip()
                link = "https://finance.naver.com" + title_td.a['href']
                date_td = tr.select_one('.date')
                date_str = date_td.text.strip() if date_td else ""
                news_list.append({'title': title, 'link': link, 'date': date_str})
                if len(news_list) >= 5:
                    break
        return news_list
    except Exception as e:
        print(f"뉴스 조회 오류 ({symbol}): {e}")
        return []
