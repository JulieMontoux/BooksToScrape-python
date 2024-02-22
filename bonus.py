import csv
from collections import defaultdict
import matplotlib.pyplot as plt

# Fonction pour lire le fichier CSV généré par generate_books_details_by_category
def read_books_details_csv(filename='books_details_by_category.csv'):
    category_details = defaultdict(dict)
    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            category = row['category']
            books_count = int(row['books_count'])
            average_price = float(row['average_price'])
            category_details[category] = {'books_count': books_count, 'average_price': average_price}
    return category_details

# Afficher le diagramme circulaire du nombre de livres par catégorie
def plot_books_count_pie_chart(category_details):
    sorted_categories = sorted(category_details.items(), key=lambda x: x[1]['books_count'], reverse=True)
    labels = [category[0] for category in sorted_categories[:20]]
    sizes = [category[1]['books_count'] for category in sorted_categories[:20]]
    plt.figure(figsize=(10, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Nombres de livres par catégorie (20 premières catégories)')
    plt.axis('equal')
    plt.tight_layout()
    plt.show()

# Afficher l'histogramme des prix moyens des livres par catégorie
def plot_average_price_histogram(category_details):
    labels = category_details.keys()
    average_prices = [details['average_price'] for details in category_details.values()]
    plt.figure(figsize=(10, 6))
    plt.bar(labels, average_prices, color='skyblue')
    plt.xlabel('Catégorie')
    plt.ylabel('Prix moyen')
    plt.title('Prix moyen des livres par catégorie')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    category_details = read_books_details_csv()

    plot_books_count_pie_chart(category_details)
    plot_average_price_histogram(category_details)
