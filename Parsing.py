import requests
from bs4 import BeautifulSoup

def get_categories(url):
    """
    Получает категории с указанного URL.

    :param url: URL страницы каталога.
    :return: Список категорий, найденных на странице.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    categories = soup.find_all('li', class_='sect')
    return categories

def get_pages(url):
    """
    Определяет количество страниц пагинации на указанной странице.

    :param url: URL страницы категории.
    :return: Максимальное количество страниц.
    """
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

def get_items(url):
    """
    Получает список товаров с указанной страницы.

    :param url: URL страницы с товарами.
    :return: Список элементов товаров.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    item_titles = soup.find_all('div', class_='item-title')
    return item_titles

def get_product_info(url):
    """
    Извлекает информацию о продукте с указанного URL.

    :param url: URL страницы продукта.
    """
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

        # Поиск всех изображений товара
        images_slider = [img['src'] for img in soup.select('div.item_slider img')]
        images_thumbs = [img['src'] for img in soup.select('div.thumbs img')]

        # Если нет изображений в 'thumbs', ищем в 'offers_img wof'
        if not images_thumbs:
            images_thumbs = [a['href'] for a in soup.select('div.offers_img.wof a')]

        # Объединяем все ссылки на изображения
        images = images_slider + images_thumbs

        # Удаляем дубликаты изображений
        images_set = set()
        images_unique = []
        for image in images:
            base_url = "https://yacht-parts.ru"
            if not image.startswith(base_url):
                image = base_url + image
            image_name = image.split('/')[-1]
            if image_name not in images_set:
                images_set.add(image_name)
                images_unique.append(image)

        # Выводим уникальные ссылки на изображения
        images = images_unique
        print(', '.join(images))

def main():
    """
    Основная функция, которая запускает процесс сбора данных.
    """
    base_url = "https://yacht-parts.ru"
    categories_url = "https://yacht-parts.ru/catalog/"
    categories = get_categories(categories_url)
    for category in categories:
        category_url = base_url + category.find('a')['href']
        print(f"Категория: {category.find('a').text}")
        max_page = get_pages(category_url)
        for page in range(1, max_page + 1):
            page_url = f"{category_url}?PAGEN_1={page}"
            item_titles = get_items(page_url)
            for item_title in item_titles:
                product_url = base_url + item_title.find('a')['href']
                print(f"  Товар: {item_title.find('a').text}")
                get_product_info(product_url)

if __name__ == "__main__":
    main()
