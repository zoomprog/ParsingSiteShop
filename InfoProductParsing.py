import requests
from bs4 import BeautifulSoup

url = "https://yacht-parts.ru/catalog/exterior/yakornoe/yakornyy_vertlyug_dvoynoy_osculati_iz_316_morskoy_nerzhaveyushchey_stali/"

response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    # Поиск цены
    price_element = soup.select_one('.cost .price')
    if price_element:
        price = price_element.text.strip()
        print('Цена:', price)
    else:
        print("Элемент цены не найден")

    # Поиск артикула
    article_element = soup.select_one('.article.iblock .value')
    if article_element:
        article = article_element.text.strip()
        print('Артикул:', article)
    else:
        print("Элемент артикула не найден")



# Поиск первого элемента с классом 'detail_text'
first_detail_text_element = soup.select_one('div.preview_text')

# Проверка и вывод текста
if first_detail_text_element:
    detail_text = first_detail_text_element.text.strip()
    print('Описание:', detail_text)
else:
    print("Элемент с классом 'detail_text' не найден")

# Поиск всех элементов <a> внутри <div class="offers_img wof">
links = [a['href'] for a in soup.select('div.offers_img.wof a')]

# Вывод ссылок через запятую
print(', '.join(links))