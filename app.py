from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import random
import concurrent.futures

app = Flask(__name__)

def get_product_data(product_page):
    try:
        response = requests.get(product_page)
        soup = BeautifulSoup(response.text, 'lxml')
        name = soup.find("span",attrs={"id":'productTitle'}).text.strip()
        price = soup.find("span",attrs={'class':'a-offscreen'}).text.strip()
        rating = soup.find("span",attrs={'class':'a-icon-alt'}).text.strip()
        image = soup.find("div",attrs={'class':'imgTagWrapper'}).find('img').get('src')
        return {
            'name': name,
            'price': price,
            'rating': rating,
            'image': image
        }
    except Exception as e:
        return None

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        search_term = request.args.get('search_term',type=str)
        url = f'https://www.amazon.in/s?k={search_term}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        links = soup.find_all("a",attrs={'class':'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})
        product_pages = ["https://amazon.in" + link.get('href') for link in links]

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_product_data, product_page) for product_page in product_pages]
            products = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        products = [product for product in products if product is not None]

        return jsonify(random.sample(products, min(5, len(products))))
    except Exception as e:
        return jsonify(e)

if __name__ == '__main__':
    app.run(debug=True)
