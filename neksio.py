from selenium import webdriver
from selenium.webdriver.firefox.options import Options  # For headless mode
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import re
import time

# Setup headless browser
options = Options()
options.headless = True  # Run Firefox in headless mode
browser = webdriver.Firefox(options=options)  
wait = WebDriverWait(browser, 20)

categories = {
    "Motherboard": "https://g.store.neksio.mk/Shop?CategoryId=18",
}

all_products = []
seen_product_links = set()  

def scrape_category(category, url):
    print(f"Navigating to: {url}")
    browser.get(url)

    time.sleep(3)  # Wait for page load
    print(f"Current URL after load: {browser.current_url}")

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.custom-card-grid")))
        print(f"Category page for {category} loaded successfully.")
    except Exception as e:
        print(f"Error while waiting for page to load: {e}")
        return

    last_height = browser.execute_script("return document.body.scrollHeight")
    
    while True:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  

        items = browser.find_elements(By.CSS_SELECTOR, "div.custom-card-grid")
        print(f"Found {len(items)} items in {category}.")

        for item in items:
            try:
                title = item.find_element(By.CSS_SELECTOR, "div.product-name-wrapper p.name").text.strip()
                product_link = item.find_element(By.CSS_SELECTOR, "h3.product-title a").get_attribute('href')

                if product_link not in seen_product_links:
                    code = item.find_element(By.CSS_SELECTOR, "div.product-name-wrapper .product-code").text.strip()
                    price = item.find_element(By.CSS_SELECTOR, "div.price-container .price").text.strip()
                    price = int(re.sub(r"[^\d]", "", price))
                    image = item.find_element(By.CSS_SELECTOR, "img.product-image").get_attribute("src")
                    manufacturer = item.find_element(By.CSS_SELECTOR, "div.product-manufacturer-wrapper .manufacturer").text.strip()

                    all_products.append({
                        "Title": title,
                        "Manufacturer": manufacturer,
                        "Price": price,
                        "Code": code,
                        "Warranty": "warranty",
                        "Link": product_link,
                        "Category": category,
                        "Description": "description",
                        "Image": image,
                        "Store": "Neksio"
                    })
                    seen_product_links.add(product_link)
                else:
                    print(f"Duplicate product found: {product_link}. Skipping.")
            except Exception as e:
                print(f"Error extracting {category} data: {e}")

        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("No more new products loaded. Exiting scraping loop.")
            break  

        last_height = new_height 

# Loop through all categories and scrape them
for category, url in categories.items():
    scrape_category(category, url)

df = pd.DataFrame(all_products)
df.to_csv("neksio_products.csv", index=False, encoding="utf-8")
print(f"All data saved to neksio_products.csv. Total products scraped: {len(all_products)}")

browser.quit()