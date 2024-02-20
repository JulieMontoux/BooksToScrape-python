import os
import requests
from bs4 import BeautifulSoup
import csv
import time
from urllib.parse import urljoin

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

def scrape_book_details(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        books = soup.find_all('h3')
        
        all_books_data = []
        
        for book in books:
            book_url = book.find('a')['href']
            book_full_url = urljoin(url, book_url)
            
            book_data = scrape_book_info(book_full_url)
            if book_data:
                all_books_data.append(book_data)
            
            time.sleep(1)
        
        return all_books_data
    else:
        print("Failed to retrieve page:", url)
        return None

def scrape_book_info(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        product_page_url = url
        title = soup.find('h1').text.strip()
        upc = soup.select_one('th:-soup-contains("UPC") + td').text.strip()
        price_including_tax = soup.select_one('th:-soup-contains("Price (incl. tax)") + td').text.strip()[1:]
        price_excluding_tax = soup.select_one('th:-soup-contains("Price (excl. tax)") + td').text.strip()[1:]
        availability = soup.select_one('th:-soup-contains("Availability") + td').text.strip()
        product_description = soup.find('meta', {'name': 'description'})['content']
        category = soup.find('ul', class_='breadcrumb').find_all('a')[2].text.strip()
        review_rating = soup.find('p', class_='star-rating')['class'][1]
        image_url = soup.find('img')['src']

        image_url = urljoin(url, image_url)
        
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
        print("Failed to retrieve page:", url)
        return None

def write_to_csv(data, category_name):
    directory = 'scraped_books'
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    filename = f'{directory}/{category_name}_books.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for item in data:
            writer.writerow(item)

if __name__ == "__main__":
    base_url = "http://books.toscrape.com/catalogue/category/books_1/index.html"
    category_urls = scrape_categories(base_url)

    for category_url in category_urls:
        category_name = category_url.split('/')[-2]
        books_data = scrape_book_details(category_url)
        if books_data:
            write_to_csv(books_data, category_name)
            print(f"Scraping completed successfully for category: {category_name}.")