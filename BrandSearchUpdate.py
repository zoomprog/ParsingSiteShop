import requests
import json
from bs4 import BeautifulSoup

# Базовый URL-адрес страницы бренда
base_url = "https://yacht-parts.ru"

# Функция получения количества страниц
def get_max_page(soup):
    pagination = soup.find('div', class_='module-pagination')
    if pagination:
        pages = pagination.find('span', class_='nums')
        if pages:
            page_links = pages.find_all('a')
            if page_links:
                return int(page_links[-1].text.strip())
    return 1

# Функция для извлечения названий продуктов со страницы
def extract_product_names(soup):
    item_titles = soup.find_all('div', class_='item-title')
    product_names = []
    for item_title in item_titles:
        span = item_title.find('span')
        if span:
            product_names.append(span.text.strip())
    return product_names

# Получить список брендов
url = f"{base_url}/info/brands/"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

brands_list = soup.find('ul', class_='brands_list')
brands = brands_list.find_all('li')

data = []

# Перебрать каждый бренд
for brand in brands:
    link = brand.find('a')
    brand_url = base_url + link.get('href')
    brand_response = requests.get(brand_url)
    brand_soup = BeautifulSoup(brand_response.text, 'html.parser')

    # Извлечь название бренда из тега <h1>
    brand_name_tag = brand_soup.find('h1', id='pagetitle')
    if brand_name_tag:
        brand_name = brand_name_tag.text.strip()
    else:
        continue

    # Распечатайте название бренда
    print(f"Brand: {brand_name}")

    # Получить количество страниц
    max_page = get_max_page(brand_soup)

    # Перебирать каждую страницу
    for page in range(1, max_page + 1):
        page_url = f"{brand_url}?PAGEN_1={page}"
        page_response = requests.get(page_url)
        page_soup = BeautifulSoup(page_response.text, 'html.parser')

        # Извлечение и печать названий продуктов
        product_names = extract_product_names(page_soup)
        for product_name in product_names:
            print(f"  - {product_name}")
            data.append({
                "brand": brand_name,
                "product": product_name
            })

# Записать данные в JSON файл
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
