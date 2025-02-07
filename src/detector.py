import requests
from bs4 import BeautifulSoup
import os
from playwright.sync_api import sync_playwright

PRODUCT_TEST_URL = "https://amaialondon.com/products/blue-baby-girl-shoes"
LOG_FILE = "logs/content_loading.txt"

def check_static_html(url):
    """Check if product data is present in the raw HTML."""
    print(f"🔍 Checking static HTML for: {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch product page: {e}")
        return False

    soup = BeautifulSoup(response.text, "html.parser")

    # Look for key elements (title, price, sizes, images)
    title = soup.find("h1")
    price = soup.find(class_="price")
    images = soup.find_all("img")

    if title and price and images:
        print("✅ Product data found in static HTML!")
        log_result("STATIC_HTML", url)
        return True
    else:
        print("⚠️ Product data missing in static HTML, checking JavaScript...")
        return False

def check_javascript_loading(url):
    """Use Playwright to check if product data loads dynamically via JavaScript."""
    print(f"🔍 Checking JavaScript rendering for: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="load")

        html_content = page.content()
        with open("logs/page_source.html", "w") as f:
            f.write(html_content)
        print("✅ Saved rendered page source to logs/page_source.html")

        # Check if key elements exist after rendering
        title = page.locator("h1").text_content() if page.locator("h1").count() > 0 else None
        price = page.locator(".price").text_content() if page.locator(".price").count() > 0 else None
        images = page.locator("img").all()

        browser.close()

        if title and price and images:
            print("✅ Product data loaded via JavaScript!")
            log_result("JAVASCRIPT", url)
            return True
        else:
            print("⚠️ No product data found after JavaScript execution.")
            return False

def detect_api_for_product(product_url):
    """Check if a JSON API endpoint exists for a given product URL."""
    if not product_url.startswith("http"):
        print(f"❌ Invalid product URL: {product_url}")
        return None  # Invalid URL detected
    
    api_url = product_url + ".json"
    print(f"🔍 Checking API endpoint: {api_url}")

    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200 and response.headers.get("Content-Type", "").startswith("application/json"):
            print(f"✅ API detected! Using {api_url} for product data.")
            return api_url  # Return API endpoint if detected
        else:
            print(f"⚠️ No API found for {product_url}, using HTML parsing instead.")
            return None  # No API detected, fall back to HTML
    except requests.RequestException as e:
        print(f"❌ Error checking API: {e}")
        return None  # Handle connection errors gracefully

def log_result(method, url):
    """Log how the content is being loaded."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"{method}: {url}\n")

if __name__ == "__main__":
    # Step 1: Check if static HTML contains product data
    if not check_static_html(PRODUCT_TEST_URL):
        # Step 2: Check if JavaScript is required
        check_javascript_loading(PRODUCT_TEST_URL)
