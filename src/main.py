# import os
# import psycopg2

# def test_db_connection():
#     try:
#         conn = psycopg2.connect(
#             dbname=os.getenv("DB_NAME"),
#             user=os.getenv("DB_USER"),
#             password=os.getenv("DB_PASSWORD"),
#             host=os.getenv("DB_HOST"),
#             port=os.getenv("DB_PORT"),
#         )
#         cursor = conn.cursor()
#         cursor.execute("SELECT 1;")
#         print("✅ PostgreSQL is connected and working!")
#         cursor.close()
#         conn.close()
#     except Exception as e:
#         print(f"❌ Database connection failed: {e}")

# if __name__ == "__main__":
#     test_db_connection()


import os
import psycopg2
import pandas as pd
from scraper import process_sitemaps, crawl_all_products, crawl_product
from storage import DB_CONFIG

def verify_database():
    """Check if the database is running and the 'products' table exists, and recreate it if needed."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Drop and recreate table to ensure latest schema
        print("⚠️ Dropping and recreating 'products' table to ensure schema consistency...")
        cursor.execute("DROP TABLE IF EXISTS products;")
        cursor.execute("""
            CREATE TABLE products (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL UNIQUE,
                descriptions TEXT,  -- Ensure descriptions column exists
                variants TEXT,
                price TEXT NOT NULL,
                sizes TEXT,
                colors TEXT,
                images TEXT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        print("✅ 'products' table recreated successfully.")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def verify_sitemap_extraction():
    """Check if sitemap extraction generates a valid product URL list."""
    process_sitemaps()
    if not os.path.exists("data/product_urls.csv"):
        print("❌ product_urls.csv not found after sitemap extraction.")
        return False
    df = pd.read_csv("data/product_urls.csv")
    if "Product URL" not in df.columns or df.empty:
        print("❌ product_urls.csv is empty or incorrectly formatted.")
        return False
    print(f"✅ Sitemap extracted {len(df)} product URLs correctly.")
    return True

def test_single_product_crawl():
    """Test crawling a single product to verify data extraction."""
    test_url = "https://amaialondon.com/products/blue-baby-girl-shoes"
    product_data = crawl_product(test_url)
    if product_data:
        print("✅ Successfully crawled single product.")
        return True
    else:
        print("❌ Failed to crawl single product.")
        return False

def check_data_storage():
    """Check if data has been saved correctly in CSV and database."""
    if not os.path.exists("data/products.csv"):
        print("❌ products.csv not found.")
        return False
    df = pd.read_csv("data/products.csv")
    if df.empty:
        print("❌ products.csv is empty.")
        return False
    print(f"✅ products.csv contains {len(df)} products.")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products;")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        if count > 0:
            print(f"✅ Database contains {count} products.")
            return True
        else:
            print("❌ Database has no product entries.")
            return False
    except Exception as e:
        print(f"❌ Database query failed: {e}")
        return False

def main():
    """Run full verification and crawling pipeline."""
    print("🚀 Starting full pipeline check...")
    
    if not verify_database():
        print("❌ Database verification failed. Exiting.")
        return
    
    if not verify_sitemap_extraction():
        print("❌ Sitemap extraction failed. Exiting.")
        return
    
    if not test_single_product_crawl():
        print("❌ Single product crawl failed. Exiting.")
        return
    
    if not check_data_storage():
        print("❌ Data storage check failed. Exiting.")
        return
    
    print("✅ All checks passed. Running full crawl...")
    crawl_all_products()
    print("✅ Full pipeline completed successfully!")

if __name__ == "__main__":
    main()
