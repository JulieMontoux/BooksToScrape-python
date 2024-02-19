import requests
from bs4 import BeautifulSoup
import csv
import time

def scrape_book_details(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        books = soup.find_all('h3') 
        
        all_books_data = []
        
        for book in books:
            book_url = book.find('a')['href']
            book_full_url = url.rsplit('/', 1)[0] + '/' + book_url
            
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
        upc = soup.find('th', text='UPC').find_next('td').text.strip()
        price_including_tax = soup.find('th', text='Price (incl. tax)').find_next('td').text.strip()[1:]
        price_excluding_tax = soup.find('th', text='Price (excl. tax)').find_next('td').text.strip()[1:]
        availability = soup.find('th', text='Availability').find_next('td').text.strip()
        product_description = soup.find('meta', {'name': 'description'})['content']
        category = soup.find('ul', class_='breadcrumb').find_all('a')[2].text.strip()
        review_rating = soup.find('p', class_='star-rating')['class'][1]
        image_url = soup.find('img')['src']
        
        availability_text = availability.split('(')[-1].split()[0]
        if availability_text == "In":
            number_available = availability.split()[0]
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

def write_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for item in data:
            writer.writerow(item)

if __name__ == "__main__":
    category_url = "http://books.toscrape.com/catalogue/category/books/mystery_3/index.html"
    
    all_books_data = []
    page_num = 1
    while True:
        url = category_url if page_num == 1 else category_url.replace('index.html', f'page-{page_num}.html')
        page_books_data = scrape_book_details(url)
        if not page_books_data:
            break
        all_books_data.extend(page_books_data)
        page_num += 1
    
    write_to_csv(all_books_data, 'scraped_books_category.csv')
    print("Scraping completed successfully.")
