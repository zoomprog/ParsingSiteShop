import os
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Функция для получения категорий с указанного URL
def get_categories(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    categories = soup.find_all('li', class_='sect')
    return categories

# Функция для получения количества страниц пагинации
def get_pages(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
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
    return max_page

# Функция для получения элементов товаров на странице
def get_items(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    item_titles = soup.find_all('div', class_='item-title')
    return item_titles

# Функция для получения информации о продукте с указанного URL
def get_product_info(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Извлечение цены
        price_element = soup.select_one('.cost .price')
        price = price_element.text.strip() if price_element else "Не найдено"

        # Извлечение артикула
        article_element = soup.select_one('.article.iblock .value')
        article = article_element.text.strip() if article_element else "Не найдено"

        # Извлечение описания
        first_detail_text_element = soup.select_one('div.preview_text')
        detail_text = first_detail_text_element.text.strip() if first_detail_text_element else "Не найдено"

        # Извлечение URL изображений
        images_slider = [img['src'] for img in soup.select('div.item_slider img')]
        images_thumbs = [img['src'] for img in soup.select('div.thumbs img')]

        if not images_thumbs:
            images_thumbs = [a['href'] for a in soup.select('div.offers_img.wof a')]

        images = images_slider + images_thumbs

        images_set = set()
        images_unique = []
        base_url = "https://yacht-parts.ru"
        for image in images:
            if not image.startswith(base_url):
                image = base_url + image
            image_name = image.split('/')[-1]
            if image_name not in images_set:
                images_set.add(image_name)
                images_unique.append(image)

        images_urls = ', '.join(images_unique)

        return {
            'Цена': price,
            'Артикул': article,
            'Описание': detail_text,
            'Картинки': images_urls
        }
    except requests.exceptions.Timeout:
        print(f"Timeout occurred for URL: {url}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    return None

# Функция для извлечения бренда из названия продукта
def extract_brand(product_name):
    match = re.search(r"\b[A-Za-z]{3,}\b", product_name)
    if match:
        return match.group(0)
    return "Не найдено"

# Функция для сохранения данных в Excel файл
def save_to_excel(data, file_path):
    df = pd.DataFrame(data)
    if os.path.exists(file_path):
        existing_df = pd.read_excel(file_path)
        df = pd.concat([existing_df, df], ignore_index=True)
        with pd.ExcelWriter(file_path, mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name='Все данные', index=False)
    else:
        with pd.ExcelWriter(file_path, mode='w') as writer:
            df.to_excel(writer, sheet_name='Все данные', index=False)

# Основная функция программы
def main():
    base_url = "https://yacht-parts.ru"
    categories_url = "https://yacht-parts.ru/catalog/"
    categories = get_categories(categories_url)

    file_path = 'products.xlsx'

    # Загрузка существующих категорий из Excel файла, если он существует
    existing_categories = set()
    if os.path.exists(file_path):
        existing_df = pd.read_excel(file_path, usecols=['Категория'])
        existing_categories = set(existing_df['Категория'].unique())

    all_data = []

    for category in categories:
        category_name = category.find('a').text
        if category_name in existing_categories:
            print(f"Категория '{category_name}' уже существует в файле. Пропуск...")
            continue

        print(f"\033[91mОбработана категория: {category_name}\033[0m")

        category_url = base_url + category.find('a')['href']
        max_page = get_pages(category_url)

        for page in range(1, max_page + 1):
            page_url = f"{category_url}?PAGEN_1={page}"
            item_titles = get_items(page_url)
            for item_title in item_titles:
                product_name = item_title.find('a').text
                print(f"\033[92mОбработанный продукт: {product_name}\033[0m")
                product_url = base_url + item_title.find('a')['href']
                product_info = get_product_info(product_url)
                if product_info:
                    brand_name = extract_brand(product_name)
                    all_data.append({
                        'Категория': category_name,
                        'Название товара': product_name,
                        'Бренд': brand_name,
                        **product_info
                    })

        if all_data:
            save_to_excel(all_data, file_path)
            # Очистка данных после сохранения, чтобы избежать дублирования
            all_data = []

if __name__ == "__main__":
    main()
