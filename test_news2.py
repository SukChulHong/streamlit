import requests
from bs4 import BeautifulSoup

url = "https://finance.naver.com/item/news_news.naver?code=005930&page=1"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Referer': 'https://finance.naver.com/item/news.naver?code=005930'
}
res = requests.get(url, headers=headers)
res.encoding = 'euc-kr'
soup = BeautifulSoup(res.text, 'html.parser')

# Naver finance news usually has table class 'type5'
table = soup.select('.type5 tbody tr')
print(f"Rows in .type5 tbody tr: {len(table)}")
for i, tr in enumerate(table[:3]):
    print(tr.text.strip()[:100])
