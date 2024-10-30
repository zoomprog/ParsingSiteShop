import requests
from bs4 import BeautifulSoup

url = "https://yacht-parts.ru/catalog/exterior/yakornoe/"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Находим количество страниц
pagination = soup.find('div', class_='module-pagination')
if pagination:
    pages = pagination.find('span', class_='nums')
    if pages:
        pages = pages.find_all('a')
        if pages:
            max_page = int(pages[-1].text.strip())
        else:
            max_page = 1
    else:
        max_page = 1
else:
    max_page = 1

# Переходим по страницам и выводим текст внутри тегов <span>
for page in range(1, max_page + 1):
    page_url = f"{url}?PAGEN_1={page}"
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    item_titles = soup.find_all('div', class_='item-title')
    for item_title in item_titles:
        span_text = item_title.find('span').text.strip()
        print(span_text)
