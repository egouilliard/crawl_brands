import csv
import os
import psycopg2

DATA_DIR = "data"
PRODUCTS_DATA_CSV = os.path.join(DATA_DIR, "products.csv")  # Data storage CSV


DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "amaia_db"),
    "user": os.getenv("DB_USER", "amaia_user"),
    "password": os.getenv("DB_PASSWORD", "amaia_pass"),
    "host": os.getenv("DB_HOST", "db"),
    "port": os.getenv("DB_PORT", "5432"),
}

def save_product_to_csv(product_data):
    """Save extracted product data to a CSV file."""
    os.makedirs(DATA_DIR, exist_ok=True)

    file_exists = os.path.isfile(PRODUCTS_DATA_CSV)
    with open(PRODUCTS_DATA_CSV, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # Write header only if file is new
        if not file_exists:
            writer.writerow(["Title", "descriptions", "Price", "Variants", "Images"])

        writer.writerow([
            product_data.get("title"),
            product_data.get("body_html"),
            product_data.get("variants", [{}])[0].get("price"),
            "; ".join([variant["title"] for variant in product_data.get("variants", [])]),
            "; ".join([img["src"] for img in product_data.get("images", [])]),
        ])

    print(f"✅ Product saved to CSV: {product_data.get('title')}")

def save_product_to_db(product_data):
    """Save extracted product data to PostgreSQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                title TEXT,
                descriptions TEXT,
                price TEXT,
                variants TEXT,
                images TEXT
            );
        """)

        # Insert product data
        cursor.execute("""
            INSERT INTO products (title, descriptions, price, variants, images)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (title) DO UPDATE
            SET descriptions = EXCLUDED.descriptions,
                price = EXCLUDED.price,
                variants = EXCLUDED.variants,
                images = EXCLUDED.images;
        """, (
            product_data.get("title"),
            product_data.get("body_html"),
            product_data.get("variants", [{}])[0].get("price"),
            "; ".join([variant["title"] for variant in product_data.get("variants", [])]),
            "{" + ",".join([f'"{img["src"]}"' for img in product_data.get("images", [])]) + "}"  # ✅ Correct array format
        ))


        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Product saved to PostgreSQL: {product_data.get('title')}")
    except Exception as e:
        print(f"❌ Failed to save product to database: {e}")
