import requests
import xml.etree.ElementTree as ET
import os
import csv
import pandas as pd
from detector import detect_api_for_product  # Import from detector.py
from storage import save_product_to_csv, save_product_to_db


SITEMAP_URL = "https://amaialondon.com/sitemap.xml"
DATA_DIR = "data"
SITEMAP_CSV = os.path.join(DATA_DIR, "sitemap_urls.csv")
PRODUCTS_CSV = os.path.join(DATA_DIR, "products.csv")
COLLECTIONS_CSV = os.path.join(DATA_DIR, "collections.csv")
PRODUCTS_URLS_CSV = os.path.join(DATA_DIR, "product_urls.csv")  # Separate file for URLs

def crawl_product(product_url):
    """Crawl product details using API if available, otherwise use HTML parsing."""
    api_url = detect_api_for_product(product_url)

    if api_url:
        # API detected, fetch product details from JSON
        response = requests.get(api_url)
        product_data = response.json().get("product", {})
        print(f"✅ Extracted product data from API: {product_data['title']}")

        # Save product data
        save_product_to_csv(product_data)
        save_product_to_db(product_data)
        return product_data

    else:
        # No API detected, fall back to HTML scraping
        print(f"⚠️ Crawling {product_url} via HTML parsing...")
        return None

def crawl_all_products():
    """Crawl all products found in the sitemap and store the data."""
    print("🔍 Crawling all product pages...")

    if not os.path.exists(PRODUCTS_URLS_CSV):
        print("❌ No product URLs found. Run process_sitemaps() first.")
        return

    df = pd.read_csv(PRODUCTS_URLS_CSV)

    if "Product URL" not in df.columns:
        print("❌ Column 'Product URL' not found in CSV. Check file format.")
        return

    product_urls = df["Product URL"].dropna().str.strip().tolist()

    if not product_urls:
        print("❌ No valid product URLs found. Check product_urls.csv format.")
        return

    print(f"First 10 product URLs: {product_urls[:10]}")
    print(f"✅ Found {len(product_urls)} products to crawl.")

    for idx, url in enumerate(product_urls, start=1):
        print(f"➡️ Crawling ({idx}/{len(product_urls)}): {url}")
        crawl_product(url)

    print("✅ Finished crawling all products!")

def fetch_sitemap():
    """Fetch and parse the main sitemap.xml file."""
    print(f"Fetching sitemap from {SITEMAP_URL}...")

    try:
        response = requests.get(SITEMAP_URL, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch sitemap: {e}")
        return []

    try:
        root = ET.fromstring(response.content)
        urls = [elem.text for elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        print(f"✅ Found {len(urls)} sub-sitemaps.")
        return urls
    except ET.ParseError as e:
        print(f"❌ Failed to parse sitemap XML: {e}")
        return []

def fetch_sub_sitemap(url):
    """Fetch and parse a sub-sitemap."""
    print(f"Fetching sub-sitemap: {url}...")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch sub-sitemap: {e}")
        return []

    try:
        root = ET.fromstring(response.content)
        urls = [elem.text for elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        return urls
    except ET.ParseError as e:
        print(f"❌ Failed to parse sub-sitemap XML: {e}")
        return []

def classify_url(url):
    """Classify URLs based on patterns (product, collection, blog, etc.)."""
    if "/products/" in url:
        return "Product"
    elif "/collections/" in url:
        return "Collection"
    elif "/blogs/" in url:
        return "Blog"
    elif "/pages/" in url:
        return "Page"
    return "Other"

def process_sitemaps():
    """Fetch and analyze all sub-sitemaps, classifying URLs."""
    os.makedirs(DATA_DIR, exist_ok=True)
    sitemap_urls = fetch_sitemap()
    
    all_urls = []
    classified_urls = {
        "Product": [],
        "Collection": [],
        "Blog": [],
        "Page": [],
        "Other": []
    }

    for sitemap in sitemap_urls:
        sub_urls = fetch_sub_sitemap(sitemap)
        all_urls.extend(sub_urls)

        for url in sub_urls:
            category = classify_url(url)
            classified_urls[category].append(url)

    # Save extracted URLs by category
    save_urls_to_csv(PRODUCTS_URLS_CSV, classified_urls["Product"], ["Product URL"])
    save_urls_to_csv(COLLECTIONS_CSV, classified_urls["Collection"], ["Collection URL"])
    
    print(f"✅ Found {len(classified_urls['Product'])} products.")
    print(f"✅ Found {len(classified_urls['Collection'])} collections.")

def save_urls_to_csv(filename, urls, header):
    """Save categorized URLs to a CSV file."""
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for url in urls:
            writer.writerow([url])

    print(f"✅ URLs saved to {filename}")

if __name__ == "__main__":
    process_sitemaps()
