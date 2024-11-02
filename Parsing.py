import os
import re
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import pandas as pd

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def get_categories(session, url):
    """
    Получает список категорий с указанного URL.
    """
    html = await fetch(session, url)
    soup = BeautifulSoup(html, 'html.parser')
    categories = soup.find_all('li', class_='sect')
    return categories

async def get_pages(session, url):
    """
    Определяет количество страниц для пагинации на указанном URL.
    """
    html = await fetch(session, url)
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find('div', class_='module-pagination')
    max_page = 1
    if pagination:
        pages = pagination.find('span', class_='nums')
        if pages:
            pages = pages.find_all('a')
            if pages:
                max_page = int(pages[-1].text.strip())
    return max_page

async def get_items(session, url):
    """
    Получает список товаров с указанной страницы.
    """
    html = await fetch(session, url)
    soup = BeautifulSoup(html, 'html.parser')
    item_titles = soup.find_all('div', class_='item-title')
    return item_titles

async def get_product_info(session, url):
    """
    Извлекает информацию о продукте с указанного URL.
    """
    try:
        html = await fetch(session, url)
        soup = BeautifulSoup(html, 'html.parser')

        price_element = soup.select_one('.cost .price')
        price = price_element.text.strip() if price_element else "Не найдено"

        article_element = soup.select_one('.article.iblock .value')
        article = article_element.text.strip() if article_element else "Не найдено"

        first_detail_text_element = soup.select_one('div.preview_text')
        detail_text = first_detail_text_element.text.strip() if first_detail_text_element else "Не найдено"

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
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

def extract_brand(product_name):
    """
    Извлекает бренд из названия продукта.
    """
    match = re.search(r"\b[A-Za-z]{3,}\b", product_name)
    if match:
        return match.group(0)
    return "Не найдено"

def save_to_excel(data, file_path):
    """
    Сохраняет данные в Excel файл.
    """
    df = pd.DataFrame(data)
    if os.path.exists(file_path):
        existing_df = pd.read_excel(file_path)
        df = pd.concat([existing_df, df], ignore_index=True)
    with pd.ExcelWriter(file_path, mode='a' if os.path.exists(file_path) else 'w', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name='Все данные', index=False)

async def main():
    """
    Основная функция для выполнения скрипта.
    """
    base_url = "https://yacht-parts.ru"
    categories_url = "https://yacht-parts.ru/catalog/"
    file_path = 'products.xlsx'

    async with aiohttp.ClientSession() as session:
        categories = await get_categories(session, categories_url)

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
            max_page = await get_pages(session, category_url)

            for page in range(1, max_page + 1):
                page_url = f"{category_url}?PAGEN_1={page}"
                item_titles = await get_items(session, page_url)
                for item_title in item_titles:
                    product_name = item_title.find('a').text
                    print(f"\033[92mОбработанный продукт: {product_name}\033[0m")
                    product_url = base_url + item_title.find('a')['href']
                    product_info = await get_product_info(session, product_url)
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
                all_data = []

if __name__ == "__main__":
    asyncio.run(main())
