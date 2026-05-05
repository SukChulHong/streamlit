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

print("Found News:")
for n in news_list:
    print(n['title'], n['date'])
