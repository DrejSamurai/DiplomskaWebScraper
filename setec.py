import cloudscraper
import time
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin

scraper = cloudscraper.create_scraper()

categories = {
    "Motherboard": "https://setec.mk/computers--it/pc-and-pc-equipment/motherboard",
    "CPU": "https://setec.mk/computers--it/pc-and-pc-equipment/processor",
    "GPU": "https://setec.mk/computers--it/pc-and-pc-equipment/graphic-cards",
    "Power Supply": "https://setec.mk/computers--it/pc-and-pc-equipment/power-supply",
    "Hard Drive": "https://setec.mk/computers--it/pc-and-pc-equipment/hard-disks",
    "Case": "https://setec.mk/computers--it/pc-and-pc-equipment/case",
    "RAM": "https://setec.mk/computers--it/pc-and-pc-equipment/ram-memory",
    "Cooler": "https://setec.mk/computers--it/pc-and-pc-equipment/coolers"
}

all_products = []

def scrape_category(category, url):
    base_url = url  
    visited_urls = set()  

    while url:
        if url in visited_urls:
            print(f"Skipping duplicate page: {url}")
            break  

        visited_urls.add(url)  

        response = scraper.get(url)

        if response.status_code != 200:
            print(f"Failed to load {category} page, status code: {response.status_code}")
            time.sleep(5)
            continue  

        soup = BeautifulSoup(response.text, "html.parser")

        items = soup.select("div.product.product-hover")
        print(f"Found {len(items)} {category}s on this page: {url}")

        for item in items:
            try:
                title_element = item.select_one("div.name a")
                title = title_element.text.strip() if title_element else "No Title"
                product_link = urljoin(base_url, title_element["href"]) if title_element else "No Link"
                
                price_element = item.select_one("span.price-new-new")
                price = price_element.text.strip() if price_element else "No Price"
                
                old_price_element = item.select_one("span.price-old-new")
                old_price = old_price_element.text.strip() if old_price_element else "No Old Price"
                
                all_products.append({
                    "Title": title,
                    "Price": price,
                    "Old Price": old_price,
                    "Link": product_link,
                    "Category": category,
                    "Store": "Setec"
                })
            except Exception as e:
                print(f"Error extracting {category} data: {e}")

        next_button = soup.select_one("ul.pagination li a[href*='?page=']")
        next_url = next_button["href"] if next_button else None

        if next_url:
            next_url = urljoin(base_url, next_url)  
            if next_url in visited_urls:  
                print(f"Next page {next_url} was already visited. Stopping pagination.")
                break
            url = next_url
        else:
            print("No more pages. Stopping pagination.")
            break  

        time.sleep(5)  

for category, url in categories.items():
    scrape_category(category, url)

df = pd.DataFrame(all_products)
df.to_csv("setec.csv", index=False, encoding="utf-8")
print("Scraping complete! Data saved to setec.csv")