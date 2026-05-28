import csv
import sys
import os
from datetime import datetime

def load_csv(filepath):
    """Load a CSV file and return (fieldnames, list-of-dicts)."""
    rows = []
    fieldnames = []
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)
    with open(filepath, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(dict(row))
    return fieldnames, rows


def save_csv(filepath, fieldnames, rows):
    """Write rows (list-of-dicts) back to a CSV file."""
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def authenticate(users):
    """Prompt for username/password and return the user dict or None."""
    print("\n" + "="*50)
    print("       GROCERY STORE MANAGEMENT SYSTEM")
    print("="*50)
    for attempt in range(3):
        username = input("\nUsername: ").strip()
        password = input("Password: ").strip()
        for user in users:
            if user['username'] == username and user['password'] == password:
                print(f"\nWelcome, {username}! (Role: {user['type']})")
                return user
        print(f"Invalid credentials. {2 - attempt} attempt(s) remaining.")
    print("Too many failed attempts. Exiting.")
    sys.exit(1)


def print_separator(char='-', width=60):
    print(char * width)


def display_grocery_map(groceries):
    """Print a compact ID → name table for cashier reference."""
    print("\n  ID  | Grocery Name")
    print_separator()
    for g in groceries:
        print(f"  {g['id']:<4}| {g['name']}")
    print_separator()


def display_groceries_table(groceries):
    """Print full grocery table with price and stock."""
    print(f"\n  {'ID':<5} {'Name':<20} {'Price':>8} {'Stock':>8}")
    print_separator()
    for g in groceries:
        print(f"  {g['id']:<5} {g['name']:<20} ${float(g['price']):>7.2f} {g['stock']:>8}")
    print_separator()

def enter_sales_transaction(transactions, groceries, trans_fields):
    """Allow user to enter a new sales transaction."""
    print("\n--- Enter Sales Transaction ---")
    display_grocery_map(groceries)

    # Build a lookup for validation
    grocery_lookup = {g['id']: g for g in groceries}

    while True:
        grocery_id = input("Enter Grocery ID: ").strip()
        if grocery_id in grocery_lookup:
            break
        print(f"  Invalid ID. Please choose from the list above.")

    grocery = grocery_lookup[grocery_id]
    print(f"  Selected: {grocery['name']}  (Price: ${float(grocery['price']):.2f})")

    while True:
        try:
            quantity = int(input("Enter quantity: ").strip())
            if quantity > 0:
                break
            print("  Quantity must be a positive integer.")
        except ValueError:
            print("  Please enter a whole number.")

    total_due = round(float(grocery['price']) * quantity, 2)
    print(f"  Total due: ${total_due:.2f}")

    while True:
        try:
            payment = float(input("Enter payment received: $").strip())
            if payment >= total_due:
                break
            print(f"  Insufficient payment. Minimum required: ${total_due:.2f}")
        except ValueError:
            print("  Please enter a valid amount.")

    change = round(payment - total_due, 2)
    now = datetime.now()
    date_str = now.strftime("%d/%m/%Y")
    time_str = now.strftime("%I:%M:%S %p")

    new_txn = {
        'date': date_str,
        'time': time_str,
        'id': grocery_id,
        'quantity': quantity,
        'payment': payment
    }
    transactions.append(new_txn)

    # Update stock
    current_stock = int(grocery['stock'])
    if current_stock >= quantity:
        grocery['stock'] = str(current_stock - quantity)
    else:
        print(f"  Warning: Stock ({current_stock}) is less than quantity sold. Stock set to 0.")
        grocery['stock'] = '0'

    print(f"\n  Transaction recorded!")
    print(f"  Change: ${change:.2f}")
    print(f"  New stock for {grocery['name']}: {grocery['stock']}")


def enter_new_grocery(groceries, grocery_fields):
    """Allow manager to add a new grocery product."""
    print("\n--- Add New Grocery Product ---")
    display_groceries_table(groceries)

    # Auto-generate next ID
    existing_ids = []
    for g in groceries:
        try:
            existing_ids.append(int(g['id']))
        except ValueError:
            pass
    next_id = str(max(existing_ids) + 1) if existing_ids else '1'
    print(f"  Auto-generated Product ID: {next_id}")

    name = input("Enter product name: ").strip()
    while not name:
        name = input("  Name cannot be empty. Enter product name: ").strip()

    while True:
        try:
            price = float(input("Enter price per item: $").strip())
            if price > 0:
                break
            print("  Price must be positive.")
        except ValueError:
            print("  Please enter a valid number.")

    while True:
        try:
            stock = int(input("Enter stock level: ").strip())
            if stock >= 0:
                break
            print("  Stock cannot be negative.")
        except ValueError:
            print("  Please enter a whole number.")

    new_grocery = {
        'id': next_id,
        'name': name,
        'price': str(price),
        'stock': str(stock)
    }
    groceries.append(new_grocery)
    print(f"\n  Product '{name}' (ID: {next_id}) added successfully.")

def show_menu(role):
    print("\n" + "="*50)
    print("               MAIN MENU")
    print("="*50)
    print("  1. Enter a sales transaction")
    if role == 'manager':
        print("  2. Add a new grocery product  [Manager]")
    print("  0. Logout and save")
    print_separator()


def run(trans_path, grocery_path, users_path='users.csv'):
    # Load files
    trans_fields, transactions = load_csv(trans_path)
    grocery_fields, groceries  = load_csv(grocery_path)
    _, users                   = load_csv(users_path)

    # Authenticate
    user = authenticate(users)
    role = user['type']

    while True:
        show_menu(role)
        choice = input("Enter choice: ").strip()

        if choice == '1':
            enter_sales_transaction(transactions, groceries, trans_fields)

        elif choice == '2' and role == 'manager':
            enter_new_grocery(groceries, grocery_fields)

        elif choice == '0':
            save_csv(trans_path, trans_fields, transactions)
            save_csv(grocery_path, grocery_fields, groceries)
            print("\n  Data saved. Goodbye!")
            break

        else:
            print("  Invalid option. Please try again.")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python grocery_store.py <transactions.csv> <groceries.csv>")
        sys.exit(1)

    trans_path   = sys.argv[1]
    grocery_path = sys.argv[2]

    # Users file sits alongside the grocery file by default
    users_dir  = os.path.dirname(grocery_path) or '.'
    users_path = os.path.join(users_dir, 'users.csv')

    run(trans_path, grocery_path, users_path)
