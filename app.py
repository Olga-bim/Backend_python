import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # Импортируем библиотеку

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Настройка логирования
file_handler = logging.FileHandler('flask_app.log')
file_handler.setLevel(logging.DEBUG)

# Формат логов с указанием времени выполнения функции
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)

app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)


# Добавляем обработчик в логгер Flask
if not app.logger.handlers:
    app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)  # Уровень логирования для приложения
# Логгируем время выполнения функции
def log_function_time(function_name):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    app.logger.info(f"Function {function_name} was called at {current_time}")


# Разрешаем запросы из других доменов
CORS(app)

db = SQLAlchemy(app)

# Модель Category (Категория)
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    products = db.relationship('Product', backref='category', lazy=True)


# Модель Product (Продукт)
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

# Функция для создания начальных данных
def create_initial_data():

    db.drop_all()
    db.create_all()

    # Начальные категории
    categories = [
        Category(name="Men's Clothing", description="A collection of stylish and comfortable clothing for men."),
        Category(name="Women's Clothing", description="Trendy and elegant clothing options for women."),
        Category(name="Kids' Clothing", description="Fun and durable clothing for children.")
    ]
    db.session.bulk_save_objects(categories)
    db.session.commit()

    # Начальные продукты
    products = [
        Product(name="Men's Casual Shirt", description="A comfortable, short-sleeve casual shirt, perfect for everyday wear.", price=25.99, category_id=1),
        Product(name="Women's Summer Dress", description="A light, floral summer dress that's perfect for warm days.", price=45.0, category_id=2),
        Product(name="Kids' T-shirt", description="A colorful t-shirt for kids, made from 100% cotton.", price=12.5, category_id=3),
        Product(name="Men's Jeans", description="Stylish and durable jeans that offer both comfort and fashion.", price=40.0, category_id=1),
        Product(name="Women's Jacket", description="A warm and fashionable jacket, ideal for cooler weather.", price=60.0, category_id=2)
    ]
    db.session.bulk_save_objects(products)
    db.session.commit()

# CRUD функции для Category (Категории)

@app.route('/categories', methods=['POST'])
def add_category():
    # Логируем время вызова функции
    log_function_time('add_category')

    # Получаем данные из запроса
    data = request.get_json()

    # Создаем новую категорию на основе данных
    new_category = Category(name=data['name'], description=data.get('description', ''))

    # Добавляем новую категорию в базу данных
    db.session.add(new_category)
    db.session.commit()

    # Возвращаем JSON-ответ об успешном добавлении категории
    return jsonify({'message': 'Category added successfully!'}), 201

@app.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    categories_list = [{'id': c.id, 'name': c.name, 'description': c.description} for c in categories]
    return jsonify(categories_list), 200

@app.route('/categories/<int:id>', methods=['PUT'])
def update_category(id):
    category = Category.query.get_or_404(id)
    data = request.get_json()
    category.name = data.get('name', category.name)
    category.description = data.get('description', category.description)
    db.session.commit()
    return jsonify({'message': 'Category updated successfully!'}), 200

@app.route('/categories/<int:id>', methods=['DELETE'])
def delete_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted successfully!'}), 200

# CRUD функции для Product (Продуктов)

@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    new_product = Product(
        name=data['name'],
        description=data.get('description', ''),
        price=data['price'],
        category_id=data['category_id']
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Product added successfully!'}), 201

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    products_list = [
        {'id': p.id, 'name': p.name, 'description': p.description, 'price': p.price, 'category': p.category.name}
        for p in products
    ]
    return jsonify(products_list), 200

@app.route('/products/category/<int:category_id>', methods=['GET'])
def get_products_by_category(category_id):
    products = Product.query.filter_by(category_id=category_id).all()
    products_list = [
        {'id': p.id, 'name': p.name, 'description': p.description, 'price': p.price, 'category': p.category.name}
        for p in products
    ]
    return jsonify(products_list), 200

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    data = request.get_json()
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)
    product.category_id = data.get('category_id', product.category_id)
    db.session.commit()
    return jsonify({'message': 'Product updated successfully!'}), 200

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully!'}), 200

if __name__ == '__main__':
    with app.app_context():
        create_initial_data()  # Создаем начальные данные
       
    app.run(debug=True)