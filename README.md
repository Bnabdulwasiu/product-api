# Product Management API

A product inventory management system that allows users to create products, track inventory with multiple unit measurements, add stock, sell products, and track sales history with profit calculation using the FIFO (First In, First Out) methodology.

## Features

- **Product Creation**: Allows users to create products with attributes like product name, quantity, selling price, cost price, category, and unit measurement.
- **Inventory Management**: Ability to add stock to existing products and track different cost prices for each batch of added products.
- **Sales Management**: Sell products in multiple unit measurements, calculate profit for each sale, and handle multiple product sales in a single transaction.
- **Sales History**: Retrieve and view a history of all sales transactions.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Bnabdulwasiu/product-api.git

2. Navigate into project directory:
   ```bash
   cd product-api
      
3. Install dependencies(using pip):
   ```bash
   pip install -r requirements.txt

4. Run migrations:
   ```bash
   python manage.py migrate

5. Start the development server:
  ```bash
  python manage.py runserver

## Usage:

