from bs4 import BeautifulSoup

with open("naver_news.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, 'html.parser')

# Naver finance news usually has table class 'type5'
table = soup.select('.type5 tbody tr')
print(f"Rows in .type5 tbody tr: {len(table)}")

for i, tr in enumerate(soup.select('.type5 tbody tr')[:5]):
    print(f"Row {i}:")
    title_td = tr.select_one('.title')
    if title_td:
        print("  Title:", title_td.text.strip())
        print("  Link:", title_td.a['href'] if title_td.a else "No link")
    date_td = tr.select_one('.date')
    if date_td:
        print("  Date:", date_td.text.strip())
    
    print("  HTML:", str(tr)[:100])
