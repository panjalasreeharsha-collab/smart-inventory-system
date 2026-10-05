import mysql.connector
from mysql.connector import Error

def get_connection():
    """Helper function to establish a database connection."""
    return mysql.connector.connect(
        host='localhost',
        database='smart_inventory',
        user='root',
        password='root'
    )

def add_category(category_name):
    """Inserts a new product category into the database."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = "INSERT INTO categories (category_name) VALUES (%s)"
        cursor.execute(query, (category_name,))
        connection.commit()
        print(f"Successfully added category: '{category_name}'")
    except Error as e:
        print(f"Error while adding category: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def add_supplier(supplier_name, contact_email):
    """Inserts a new supplier into the database."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = "INSERT INTO suppliers (supplier_name, contact_email) VALUES (%s, %s)"
        cursor.execute(query, (supplier_name, contact_email))
        connection.commit()
        print(f"Successfully added supplier: '{supplier_name}'")
    except Error as e:
        print(f"Error while adding supplier: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def add_product(product_name, category_id, supplier_id, price, stock_quantity):
    """Inserts a new product linked to a category and supplier."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = """
            INSERT INTO products (product_name, category_id, supplier_id, price, stock_quantity) 
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (product_name, category_id, supplier_id, price, stock_quantity))
        connection.commit()
        print(f"Successfully added product: '{product_name}'")
    except Error as e:
        print(f"Error while adding product: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def view_inventory():
    """Fetches and displays all products with their categories and suppliers."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = """
            SELECT p.product_id, p.product_name, c.category_name, s.supplier_name, p.price, p.stock_quantity
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
        """
        cursor.execute(query)
        products = cursor.fetchall()
        
        print("\n" + "="*80)
        print(f"{'ID':<5} | {'Product Name':<20} | {'Category':<15} | {'Supplier':<20} | {'Price':<8} | {'Stock'}")
        print("="*80)
        
        for row in products:
            prod_id, name, cat, sup, price, stock = row
            print(f"{prod_id:<5} | {name:<20} | {str(cat):<15} | {str(sup):<20} | ${price:<7.2f} | {stock}")
        
        print("="*80 + "\n")
    except Error as e:
        print(f"Error while fetching inventory: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def place_order(product_id, quantity_ordered):
    """Places an order, creates an order record, and deducts stock safely."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        # 1. Check current stock of the product
        cursor.execute("SELECT stock_quantity, product_name FROM products WHERE product_id = %s", (product_id,))
        result = cursor.fetchone()
        
        if not result:
            print(f"Error: Product with ID {product_id} not found.")
            return
            
        current_stock, product_name = result
        
        if current_stock < quantity_ordered:
            print(f"Order failed! Insufficient stock for '{product_name}'. Available: {current_stock}, Requested: {quantity_ordered}")
            return
        
        # 2. Insert into the orders table using the correct column name 'order_quantity'
        order_query = "INSERT INTO orders (product_id, order_quantity, order_status) VALUES (%s, %s, 'Completed')"
        cursor.execute(order_query, (product_id, quantity_ordered))
        
        # 3. Update the product stock
        new_stock = current_stock - quantity_ordered
        update_query = "UPDATE products SET stock_quantity = %s WHERE product_id = %s"
        cursor.execute(update_query, (new_stock, product_id))
        
        connection.commit()
        print(f"Success! Ordered {quantity_ordered} unit(s) of '{product_name}'. Remaining stock: {new_stock}")
        
    except Error as e:
        print(f"Error while processing order: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def main_menu():
    """Interactive command-line interface for the Smart Inventory System."""
    while True:
        print("\n" + "="*50)
        print("   SMART INVENTORY & ORDER MANAGEMENT SYSTEM")
        print("="*50)
        print("1. View Inventory")
        print("2. Add Category")
        print("3. Add Supplier")
        print("4. Add Product")
        print("5. Place Order")
        print("6. Exit")
        print("="*50)
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == '1':
            view_inventory()
            
        elif choice == '2':
            cat_name = input("Enter category name: ").strip()
            if cat_name:
                add_category(cat_name)
            else:
                print("Category name cannot be empty.")
                
        elif choice == '3':
            sup_name = input("Enter supplier name: ").strip()
            email = input("Enter supplier contact email: ").strip()
            if sup_name:
                add_supplier(sup_name, email)
            else:
                print("Supplier name cannot be empty.")
                
        elif choice == '4':
            try:
                p_name = input("Enter product name: ").strip()
                cat_id = int(input("Enter category ID: "))
                sup_id = int(input("Enter supplier ID: "))
                price = float(input("Enter product price (₹): "))
                stock = int(input("Enter initial stock quantity: "))
                add_product(p_name, cat_id, sup_id, price, stock)
            except ValueError:
                print("Invalid input! Please enter valid numbers for IDs, price, and stock.")
                
        elif choice == '5':
            try:
                p_id = int(input("Enter product ID to order: "))
                qty = int(input("Enter quantity to order: "))
                place_order(p_id, qty)
            except ValueError:
                print("Invalid input! Please enter a valid number for product ID and quantity.")
                
        elif choice == '6':
            print("\nExiting Smart Inventory System. Goodbye!")
            break
            
        else:
            print("Invalid choice! Please enter a number between 1 and 6.")

if __name__ == "__main__":
    main_menu()