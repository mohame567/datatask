from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import pyotp, qrcode, os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", 'mysql+pymysql://root@127.0.0.1/data_integrity')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET", "supersecret")
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=10)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

class User(db.Model):
    __tablename__ = 'users'  
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    twofa_secret = db.Column(db.String(256), nullable=False)

class Product(db.Model):
    __tablename__ = 'products'  
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.DECIMAL(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

# User Registration with 2FA Setup
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    if not all(k in data for k in ["username", "password"]):
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    twofa_secret = pyotp.random_base32()
    new_user = User(username=data['username'], password=hashed_password, twofa_secret=twofa_secret)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully", "twofa_secret": twofa_secret}), 201

# Generate QR Code 
@app.route('/2fa_qr/<username>', methods=['GET'])
def generate_qr(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    otp_uri = pyotp.totp.TOTP(user.twofa_secret).provisioning_uri(username, issuer_name="MyApp")
    img = qrcode.make(otp_uri)
    img.save(f"{username}_qrcode.png")
    return jsonify({"message": "QR code generated, check saved file"})

# Login with 2FA
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()

    if not user or not bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({"error": "Invalid credentials"}), 401
    
    totp = pyotp.TOTP(user.twofa_secret)
    if not totp.verify(data.get('2fa_code', '')):
        return jsonify({"error": "Invalid 2FA code"}), 401
    
    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token}), 200

# CRUD Operations (JWT-Protected)
@app.route('/products', methods=['POST'])
@jwt_required()
def add_product():
    data = request.json
    if not all(field in data for field in ["name", "price", "quantity"]):
        return jsonify({"error": "Missing required fields"}), 400

    new_product = Product(
        name=data['name'],
        description=data.get('description', ''),
        price=data['price'],
        quantity=data['quantity']
    )

    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Product added successfully"}), 201

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{ "id": p.id, "name": p.name, "description": p.description, "price": p.price, "quantity": p.quantity } for p in products]), 200

@app.route('/products/<int:id>', methods=['PUT'])
@jwt_required()
def update_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.json
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)
    product.quantity = data.get('quantity', product.quantity)
    
    db.session.commit()
    return jsonify({"message": "Product updated successfully"}), 200

@app.route('/products/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"}), 200

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Flask API with 2FA and JWT Authentication"})

if __name__ == '__main__':
    app.run(debug=True)
