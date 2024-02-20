import csv
from collections import defaultdict
import os

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
    root_folder = 'data'

    category_books_data = read_books_data_from_csv(root_folder)

    category_details = generate_books_details_by_category(category_books_data)

    write_books_details_csv(category_details)
