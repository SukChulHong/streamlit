import requests

url = "https://finance.naver.com/item/news_news.naver?code=005930&page=1"
headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get(url, headers=headers)
res.encoding = 'euc-kr'

with open("naver_news.html", "w", encoding="utf-8") as f:
    f.write(res.text)
