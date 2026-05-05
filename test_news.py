import requests
from bs4 import BeautifulSoup

def get_stock_news(symbol):
    url = f"https://finance.naver.com/item/news_news.naver?code={symbol}&page=1"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers)
        res.encoding = 'euc-kr' # Naver Finance is mostly euc-kr
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Check if we get blocked or if the table is empty
        table = soup.select('.type5 tbody tr')
        print(f"Found {len(table)} rows in table")
        
        news_list = []
        for tr in table:
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
        print(f"Error: {e}")
        return []

print(get_stock_news('005930'))
