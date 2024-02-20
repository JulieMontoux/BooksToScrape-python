import os
import random
import string
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import csv
import time
import concurrent.futures
from collections import defaultdict

def scrape_categories(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        categories_container = soup.find('div', class_='side_categories')
        categories_list = categories_container.find('ul').find_all('a')
        category_urls = [urljoin(url, category['href']) for category in categories_list]
        return category_urls
    else:
        print("Failed to retrieve categories from:", url)
        return []

def scrape_book_details(category_url):
    response = requests.get(category_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        books = soup.find_all('h3')  

        all_books_data = []
        
        for book in books:
            book_url = book.find('a')['href']
            book_full_url = urljoin(category_url, book_url)
            
            all_books_data.append(book_full_url)
        
        return all_books_data
    else:
        print("Failed to retrieve page:", category_url)
        return None

def scrape_book_info(book_url):
    response = requests.get(book_url)
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
        review_rating = soup.find('p', class_='star-rating')['class'][1]
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
        print("Failed to retrieve page:", book_url)
        return None

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


def download_image(image_url, category, data_dir):
    response = requests.get(image_url)
    if response.status_code == 200:
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        image_name = f"{category}_{random_string}.png"
        image_dir = os.path.join(data_dir, category, "images")
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
        image_path = os.path.join(image_dir, image_name)
        with open(image_path, 'wb') as f:
            f.write(response.content)
        print(f"Image downloaded: {image_name}")
    else:
        print("Failed to download image:", image_url)

def read_books_data_from_csv(root_folder):
    category_books_data = defaultdict(list)

    for category_folder in os.listdir(root_folder):
        category_folder_path = os.path.join(root_folder, category_folder)
        if os.path.isdir(category_folder_path):
            for file_name in os.listdir(category_folder_path):
                if file_name.endswith('.csv'):
                    file_path = os.path.join(category_folder_path, file_name)
                    with open(file_path, 'r', encoding='utf-8') as csv_file:
                        reader = csv.DictReader(csv_file)
                        for row in reader:
                            category_books_data[category_folder].append(row)

    return category_books_data

def generate_books_details_by_category(category_books_data):
    category_details = defaultdict(lambda: {'books_count': 0, 'total_price': 0})

    for category, books_data in category_books_data.items():
        for book in books_data:
            price = float(book['price_including_tax'])
            category_details[category]['books_count'] += 1
            category_details[category]['total_price'] += price

    for category, details in category_details.items():
        if details['books_count'] > 0:
            details['average_price'] = details['total_price'] / details['books_count']
        else:
            details['average_price'] = 0

    return category_details

def write_books_details_csv(category_details, filename='books_details_by_category.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['category', 'books_count', 'average_price']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for category, details in category_details.items():
            writer.writerow({'category': category,
                             'books_count': details['books_count'],
                             'average_price': details['average_price']})

if __name__ == "__main__":
    base_url = "http://books.toscrape.com/catalogue/category/books_1/index.html"
    categories_urls = scrape_categories(base_url)
    
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for category_url in categories_urls:
            category_name = category_url.split('/')[-2]
            print("Scraping category:", category_name)
            
            all_books_urls = scrape_book_details(category_url)
            if all_books_urls:
                all_books_data = list(executor.map(scrape_book_info, all_books_urls))
                
                category_dir = os.path.join(data_dir, category_name)
                if not os.path.exists(category_dir):
                    os.makedirs(category_dir)
                write_to_csv(all_books_data, category_name, data_dir)
                print(f"Scraping completed successfully for category: {category_name}.")
                for book in all_books_data:
                    download_image(book['image_url'], category_name, data_dir)

    category_books_data = read_books_data_from_csv(data_dir)
    category_details = generate_books_details_by_category(category_books_data)
    write_books_details_csv(category_details)
