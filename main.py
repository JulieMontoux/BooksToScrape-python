import os
import random
import string
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import csv
import concurrent.futures
from collections import defaultdict
import matplotlib.pyplot as plt

session = requests.Session()

# SCRAPPING CATEGORIES
def scrape_categories(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        categories_container = soup.find('div', class_='side_categories')
        categories_list = categories_container.find('ul').find_all('a')
        
        category_urls = [urljoin(url, category['href']) for category in categories_list]
        filtered_category_urls = [category_url for category_url in category_urls if not category_url.endswith('books_1/index.html')]
        
        return filtered_category_urls
    else:
        print("Échec de la récupération de la page:", url)
        return []

def scrape_book_details(category_url):
    all_books_data = []
    page_number = 1
    while True:
        response = requests.get(category_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            books = soup.find_all('h3')
            if not books:
                break
            for book in books:
                book_url = book.find('a')['href']
                book_full_url = urljoin(category_url, book_url)
                all_books_data.append(book_full_url)
            next_page_link = soup.find('li', class_='next')
            if next_page_link:
                page_number += 1
                category_url = urljoin(category_url, f"page-{page_number}.html")
            else:
                break
        else:
            print("Échec de la récupération de la page:", category_url)
            break
    return all_books_data

# SCRAPPING D UN LIVRE
def scrape_book_info(book_url):
    response = session.get(book_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        product_page_url = book_url
        title = soup.find('h1').text.strip()
        upc = soup.select_one('th:-soup-contains("UPC") + td').text.strip()
        price_including_tax = soup.select_one('th:-soup-contains("Price (incl. tax)") + td').text.strip()[1:]
        price_excluding_tax = soup.select_one('th:-soup-contains("Price (excl. tax)") + td').text.strip()[1:]
        availability = soup.select_one('th:-soup-contains("Availability") + td').text.strip()
        product_description = soup.find('meta', {'name': 'description'})['content']
        category = soup.find('ul', class_='breadcrumb').find_all('a')[2].text.strip()
        # Mapping des classes CSS à des valeurs numériques
        rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
        # Extrait la classe CSS et convertit en nombre
        review_rating_class = soup.find('p', class_='star-rating')['class'][1]
        review_rating = rating_map.get(review_rating_class, 0)  # Par défaut, 0 si la classe n'est pas trouvée
        image_url = urljoin(book_url, soup.find('img')['src'])
        start_index = availability.find('(')
        end_index = availability.find(' available)')
        if start_index != -1 and end_index != -1:
            number_available = availability[start_index + 1: end_index]
        else:
            number_available = "0"
        return {
            'product_page_url': product_page_url,
            'universal_product_code (upc)': upc,
            'title': title,
            'price_including_tax': price_including_tax,
            'price_excluding_tax': price_excluding_tax,
            'number_available': number_available,
            'product_description': product_description,
            'category': category,
            'review_rating': review_rating,
            'image_url': image_url
        }
    else:
        print("Échec de la récupération de la page:", book_url)
        return None

# ECRIT DANS LE CSV (CATEGORIES)
def write_to_csv(data, category, data_dir):
    filename = f'scraped_books_{category}.csv'
    category_dir = os.path.join(data_dir, category)
    if not os.path.exists(category_dir):
        os.makedirs(category_dir)
    file_path = os.path.join(category_dir, filename)
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames) 
        writer.writeheader()
        for item in data:
            writer.writerow(item)

# TELECHARGEMENT DES IMAGES
def download_image(image_url, category, data_dir):
    response = session.get(image_url)
    if response.status_code == 200:
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        image_name = f"{category}_{random_string}.png"
        image_dir = os.path.join(data_dir, category, "images")
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
        image_path = os.path.join(image_dir, image_name)
        with open(image_path, 'wb') as f:
            f.write(response.content)
        print(f"Image téléchargée: {image_name}")
    else:
        print("Échec du téléchargement de l'image :", image_url)

if __name__ == "__main__":
    base_url = "http://books.toscrape.com/catalogue/category/books_1/index.html"
    categories_urls = scrape_categories(base_url)
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for category_url in categories_urls:
            category_name = category_url.split('/')[-2]
            print("Scrapping de la catégorie:", category_name)
            all_books_urls = scrape_book_details(category_url)
            if all_books_urls:
                all_books_data = list(executor.map(scrape_book_info, all_books_urls))
                category_dir = os.path.join(data_dir, category_name)
                if not os.path.exists(category_dir):
                    os.makedirs(category_dir)
                write_to_csv(all_books_data, category_name, data_dir)
                print(f"Scraping terminé avec succès pour la catégorie: {category_name}.")
                for book in all_books_data:
                    download_image(book['image_url'], category_name, data_dir)
