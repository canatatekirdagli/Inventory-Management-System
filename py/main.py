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

            date_time, _, _, product_id, _, json_data = parts

            try:
                payload = json.loads(json_data)
                for product in payload:
                    qty = product.get('qty')
                    sku = product.get('sku')
                    if qty is not None:
                        parsed_data.append((date_time, product_id, qty, sku))
            except json.JSONDecodeError as e:
                raise e

    return parsed_data


def write_to_database(data):
    with sqlite3.connect('data.db') as conn:
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS products
                        (created_at TEXT, seller_id INTEGER, qty INTEGER, sku TEXT)''')

        cursor.executemany('INSERT INTO products VALUES (?, ?, ?, ?)', data)


def generate_stock_changes():
    sku_cache = {}

    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT sku, qty FROM products ORDER BY sku, created_at')
    rows = cursor.fetchall()

    current_sku = None
    previous_qty = None
    qty_changes = []

    for row in rows:
        sku, qty = row

        if qty != previous_qty:
            if current_sku is None:
                current_sku = sku
            if sku != current_sku:
                sku_cache[current_sku] = qty_changes.copy()
                current_sku = sku
                qty_changes = []
            qty_changes.append(qty)
            previous_qty = qty

    if current_sku is not None:
        sku_cache[current_sku] = qty_changes.copy()

    sorted_sku_cache = dict(sorted(sku_cache.items(), key=lambda item: len(item[1]), reverse=True))

    with open("txt/sorted.txt", "w") as file:
        for sku, changes in sorted_sku_cache.items():
            file.write(f'{sku}: {" - ".join(map(str, changes))}\n')


def find_stable_products():
    with open("txt/sorted.txt", "r") as file:
        unchanged_products = [line.split(": ")[0] for line in file if line.count(" - ") == 0]

    with open("txt/unchanged_products.txt", "w") as file:
        file.write("\n".join(unchanged_products))


if __name__ == "__main__":
    try:
        parsed_data = process_and_parse_data('txt/firstData.txt')
        write_to_database(parsed_data)
        print("Database writing operation completed.")
        generate_stock_changes()
        print("Sorted file creation operation completed.")
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
