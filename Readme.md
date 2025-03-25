# Data Integrity (Task 1)

## Flask API with Login, 2FA, and JWT Authentication

## Overview

This project implements a **Flask API** connected to **MySQL (XAMPP)** to handle **user authentication**, **Google Authenticator-based Two-Factor Authentication (2FA)**, and **JWT-secured CRUD operations** on a `products` table.

## Features

- **User Registration with Hashed Passwords**
- **Google Authenticator (2FA) Setup via QR Code**
- **JWT-Based Authentication**
- **Secure CRUD Operations on Products**
- **Uses XAMPP MySQL as the Database**

---

## Installation & Setup

### **1️ Create Virtual Environment & Install Dependencies**

```bash
python3 -m venv venv
source venv/bin/activate  # For Linux/macOS
pip install -r requirements.txt
```

### **2️ Start MySQL in XAMPP**

```bash
sudo /opt/lampp/lampp start
```

### **3️ Set Up MySQL Database**

```sql
CREATE DATABASE data_integrity;
USE data_integrity;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(256) NOT NULL,
    twofa_secret VARCHAR(256) NOT NULL
);

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    price DECIMAL(10,2) NOT NULL,
    quantity INT NOT NULL
);
```

### **4️ Configure Environment Variables**

Create a `.env` file:

```
DATABASE_URL=mysql+pymysql://root@127.0.0.1/data_integrity
JWT_SECRET=supersecret
```

### **5️ Run Flask App**

```bash
python app.py
```

---

## API Endpoints

### **🔹 User Authentication**

#### **1️ Register User**

```http
POST /signup
```

##### **Request Body:**

```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```

##### **Response:**

```json
{
  "message": "User registered successfully",
  "twofa_secret": "JBSWY3DPEHPK3PXP"
}
```

#### **2️⃣ Generate QR Code for Google Authenticator**

```http
GET /2fa_qr/john_doe
```

##### **Response:**

```json
{
  "message": "QR code generated, check saved file"
}
```

#### **3️ Login with 2FA**

```http
POST /login
```

##### **Request Body:**

```json
{
  "username": "john_doe",
  "password": "securepassword123",
  "2fa_code": "123456"
}
```

##### **Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1..."
}
```

### **🔹 JWT-Secured Product CRUD Operations**

#### **4️ Add Product**

```http
POST /products
```

##### **Request Body:**

```json
{
  "name": "Laptop",
  "description": "Gaming Laptop",
  "price": 1200.99,
  "quantity": 10
}
```

##### **Response:**

```json
{
  "message": "Product added successfully"
}
```

#### **5️ Get All Products**

```http
GET /products
```

#### **6️ Update Product**

```http
PUT /products/1
```

##### **Request Body:**

```json
{
  "name": "Gaming Laptop",
  "price": 1300.0
}
```

##### **Response:**

```json
{
  "message": "Product updated successfully"
}
```

#### **7️ Delete Product**

```http
DELETE /products/1
```

##### **Response:**

```json
{
  "message": "Product deleted successfully"
}
```

---

## 🔧 Debugging & Troubleshooting

**1. MySQL Not Running?**

```bash
sudo /opt/lampp/lampp restart
```

**2. Database Connection Issues?**

```bash
mysql -u root -p -h 127.0.0.1
```

**3. JWT Authentication Issues?**

- Ensure you provide the JWT token in the `Authorization` header:

```
Authorization: Bearer <your_token>
```
