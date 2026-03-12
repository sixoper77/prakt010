import os
import random

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for

load_dotenv()
DEBUG = os.getenv("FLASK_DEBUG")
app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret"

products = [
    {
        "id": 1,
        "name": "Ноутбук Lenovo ThinkPad X1",
        "category": "Ноутбуки",
        "price": 45999,
        "in_stock": True,
        "description": '14" IPS, Intel Core i7, 16GB RAM, 512GB SSD',
    },
    {
        "id": 2,
        "name": 'Монітор Samsung 27" 4K',
        "category": "Монітори",
        "price": 15499,
        "in_stock": True,
        "description": '27" IPS, 3840x2160, HDR10, USB-C',
    },
    {
        "id": 3,
        "name": "Клавіатура Keychron K2",
        "category": "Периферія",
        "price": 3200,
        "in_stock": False,
        "description": "Механічна, 75%, Bluetooth, RGB",
    },
    {
        "id": 4,
        "name": "Навушники Sony WH-1000XM5",
        "category": "Аудіо",
        "price": 11999,
        "in_stock": True,
        "description": "Бездротові, ANC, 30 год автономності",
    },
    {
        "id": 5,
        "name": "Миша Logitech MX Master 3S",
        "category": "Периферія",
        "price": 4599,
        "in_stock": True,
        "description": "Бездротова, USB-C, 8000 DPI, тиха",
    },
    {
        "id": 6,
        "name": "Планшет Apple iPad Air",
        "category": "Планшети",
        "price": 27999,
        "in_stock": True,
        "description": '10.9" Liquid Retina, M1, 256GB',
    },
    {
        "id": 7,
        "name": "Веб-камера Logitech C920",
        "category": "Периферія",
        "price": 2899,
        "in_stock": False,
        "description": "Full HD 1080p, автофокус, стереомікрофон",
    },
    {
        "id": 8,
        "name": "SSD Samsung 970 EVO Plus 1TB",
        "category": "Комплектуючі",
        "price": 3899,
        "in_stock": True,
        "description": "NVMe M.2, читання 3500 МБ/с, запис 3300 МБ/с",
    },
]


def find_product(product_id):
    return next((p for p in products if p["id"] == product_id), None)


def apply_filters(product_list, category=None, min_price=None, max_price=None):
    result = product_list
    if category:
        result = [p for p in result if p["category"] == category]
    if min_price is not None:
        result = [p for p in result if p["price"] >= min_price]
    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]
    return result


@app.route("/")
def index():
    in_stock_count = sum(1 for p in products if p["in_stock"])
    return render_template("index.html", total=len(products), in_stock=in_stock_count)


@app.route("/catalog")
def catalog():
    category = request.args.get("category")
    filtered = apply_filters(products, category=category)
    categories = sorted(set(p["category"] for p in products))
    return render_template(
        "catalog.html",
        products=filtered,
        categories=categories,
        current_category=category,
        search_query=None,
    )


@app.route("/product/<int:product_id>")
def product(product_id):
    item = find_product(product_id)
    if item is None:
        return render_template("404.html", message="Товар не знайдено"), 404
    return render_template("product.html", product=item)


@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return redirect(url_for("catalog"))
    q_lower = query.lower()
    results = [
        p
        for p in products
        if q_lower in p["name"].lower() or q_lower in p["description"].lower()
    ]
    categories = sorted(set(p["category"] for p in products))
    return render_template(
        "catalog.html",
        products=results,
        categories=categories,
        current_category=None,
        search_query=query,
    )


@app.route("/random")
def random_product():
    item = random.choice(products)
    return redirect(url_for("product", product_id=item["id"]))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/api/products")
def api_products():
    category = request.args.get("category")
    min_price = request.args.get("min_price", type=int)
    max_price = request.args.get("max_price", type=int)
    result = apply_filters(
        products, category=category, min_price=min_price, max_price=max_price
    )
    return jsonify(result)


@app.route("/api/products/stats")
def api_stats():
    in_stock = [p for p in products if p["in_stock"]]
    prices = [p["price"] for p in products]
    return jsonify(
        {
            "total": len(products),
            "in_stock": len(in_stock),
            "out_of_stock": len(products) - len(in_stock),
            "categories": len(set(p["category"] for p in products)),
            "avg_price": round(sum(prices) / len(prices), 2),
            "min_price": min(prices),
            "max_price": max(prices),
        }
    )


@app.route("/api/products/<int:product_id>")
def api_product(product_id):
    item = find_product(product_id)
    if item is None:
        return jsonify({"error": "Товар не знайдено"}), 404
    return jsonify(item)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html", message="Сторінку не знайдено"), 404


if __name__ == "__main__":
    app.run(debug=DEBUG)
