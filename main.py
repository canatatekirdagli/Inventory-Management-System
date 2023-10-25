import cProfile
import re
import json
import sqlite3
import os

def process_and_parse_data(input_file):
    parsed_data = []

    with open(input_file, 'r', encoding='utf-8') as f:
        for transaction in f:
            parts = re.split(r',', transaction.strip(), maxsplit=5)
            if len(parts) < 6:
                raise ValueError("Unexpected data structure")

            _, date_time, _, seller_id, _, json_data = parts

            try:
                payload = json.loads(json_data)
                for product in payload:
                    qty = product.get('qty')
                    sku = product.get('sku')
                    if qty is not None:
                        parsed_data.append((date_time, seller_id, qty, sku))
            except json.JSONDecodeError as e:
                raise e

    return parsed_data
def write_parsed_data_to_file(data):
    with open("txt/parsedData.txt", 'w', encoding='utf-8') as f:
        for entry in data:
            date_time, seller_id, qty, sku = entry
            f.write(f"Date: {date_time}, seller_id: {seller_id}, qty: {qty}, sku: {sku}\n")
def add_data_to_database():
    with sqlite3.connect('data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS company
            (company_name TEXT, sku TEXT, value TEXT)
        ''')

        already_added_skus = set()
        with open("txt/shopList.txt", 'r', encoding='utf-8') as file:
            for line in file:
                title, sku, value = line.strip().split('\t')

                if sku in already_added_skus:
                    continue

                cursor.execute('INSERT INTO company (company_name, sku, value) VALUES (?, ?, ?)', (title, sku, value))

                already_added_skus.add(sku)
def write_to_database(data):
    with sqlite3.connect('data.db') as conn:
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS products
                        (created_at TEXT, seller_id INTEGER, qty INTEGER, sku TEXT)''')

        cursor.executemany('INSERT INTO products VALUES (?, ?, ?, ?)', data)


def generate_stock_changes():
    with sqlite3.connect('data.db') as conn:
        cursor = conn.cursor()
        cursor2 = conn.cursor()

        cursor.execute('CREATE INDEX IF NOT EXISTS products_sku_idx ON products(sku)')
        cursor2.execute('CREATE INDEX IF NOT EXISTS company_sku_idx ON company(sku)')

        cursor.execute('SELECT p.sku, p.qty '
                       'FROM products p '
                       'ORDER BY p.sku, p.created_at')

        sku_cache = {}
        current_sku = None
        previous_qty = None
        qty_changes = []

        while True:
            rows = cursor.fetchmany(1000)
            if not rows:
                break
            for row in rows:
                sku, qty = row

                if qty != previous_qty:
                    if current_sku is None:
                        current_sku = sku
                    if sku != current_sku:
                        sku_cache[current_sku] = qty_changes
                        current_sku = sku
                        qty_changes = []
                    qty_changes.append(qty)
                    previous_qty = qty

        if current_sku is not None:
            sku_cache[current_sku] = qty_changes

        sorted_sku_cache = dict(sorted(sku_cache.items(), key=lambda item: len(item[1]), reverse=True))

        with open("txt/sorted.txt", "w", encoding="utf-8") as file:
            for sku, changes in sorted_sku_cache.items():
                cursor2.execute("SELECT company_name, value FROM company WHERE sku=?", (sku,))
                result = cursor2.fetchone()

                if result is not None:
                    company, value = result
                    file.write(f'SKU: {sku}, Company Name: {company}, Value: {value}, Changes: {" - ".join(map(str, changes))}\n')
                else:
                    file.write(f'SKU: {sku}, Company Name: Data Not Found, Value: Data Not Found, Changes: {" - ".join(map(str, changes))}\n')

def find_stable_products():
    with open("txt/sorted.txt", "r", encoding="utf-8") as file:
        unchanged_products = [line.split("Changes: ")[0] for line in file if " - " not in line]
    created_at_dict = {}
    with sqlite3.connect('data.db') as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE INDEX IF NOT EXISTS sku_index ON products (sku);")

        for product in unchanged_products:
            parts = product.split(", ")
            sku = parts[0].split(": ")[1]
            company_name = parts[1].split(": ")[1]
            value = parts[2].split(": ")[1]

            cursor.execute("SELECT created_at FROM products WHERE sku=?", (sku,))
            created_at = cursor.fetchone()

            if created_at:
                created_at_dict[sku] = (created_at[0], company_name, value)

    with open("txt/unchanged_products.txt", "w", encoding="utf-8") as file:
        for sku, (created_at, company_name, value) in created_at_dict.items():
            file.write(f"SKU: {sku}, Date: {created_at}, Company Name: {company_name}, Value: {value}\n")
def calculate_stock_change(data):
    parts = data.split(", ")
    product_code = parts[0].split(": ")[1]
    company_name = parts[1].split(": ")[1]
    product_value = parts[2].split(": ")[1]

    sales = list(map(int, parts[-1].split(": ")[1].split(" - ")))
    stock_change = 0

    for i in range(len(sales)-1):
        if sales[i] > sales[i+1]:
            decrease = sales[i] - sales[i+1]
            stock_change += decrease

    return f"SKU: {product_code} Company Name: {company_name} Value: {product_value} Stock Change: {stock_change}\n"

def process_sorted_file():
    input_file_path = 'txt/sorted.txt'
    output_file_path = 'txt/totalSales.txt'

    def check_stock_decrease(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            results = []

            for line in lines:
                results.append(calculate_stock_change(line.strip()))

            return results

    results = check_stock_decrease(input_file_path)

    if results:
        with open(output_file_path, 'w',encoding="utf-8") as file:
            file.writelines(results)
    else:
        with open(output_file_path, 'w',encoding="utf-8") as file:
            pass

if __name__ == "__main__":
    try:
        parsed_data = process_and_parse_data('txt/firstData.txt')
        print("Parsing data operation completed.")
        write_parsed_data_to_file(parsed_data)
        print("Parsed Data file creation operation completed.")
        write_to_database(parsed_data)
        print("Products Database writing operation completed.")
        add_data_to_database()
        print("Company Database writing operation completed.")
        generate_stock_changes()
        print("Sorted file creation operation completed.")
        process_sorted_file()
        print("Total Sales file creation operation completed.")
        find_stable_products()
        print("Finding stable products operation completed.")
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except ValueError as e:
        print(f"Error: {e}")
    except json.JSONDecodeError as e:
        print(f"Error: JSON parsing error - {e}")
    except Exception as e:
        print(f"Error: {e}")