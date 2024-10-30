import requests
from bs4 import BeautifulSoup

url = "https://yacht-parts.ru/catalog/"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

categories = soup.find_all('li', class_='name')
subcategories = soup.find_all('li', class_='sect')

for category in categories:
    print(category.find('span').text)

for subcategory in subcategories:
    print(subcategory.find('a').text)

