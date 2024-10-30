import requests
from bs4 import BeautifulSoup

def get_categories(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    categories = soup.find_all('li', class_='sect')
    return categories

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

def get_items(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    item_titles = soup.find_all('div', class_='item-title')
    return item_titles

def main():
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
                span_text = item_title.find('span').text.strip()
                print(f"  {span_text}")

if __name__ == "__main__":
    main()
