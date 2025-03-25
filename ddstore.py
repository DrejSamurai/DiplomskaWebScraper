import cloudscraper
import time
import pandas as pd
from bs4 import BeautifulSoup

# Create a scraper that bypasses Cloudflare
scraper = cloudscraper.create_scraper()

# Define categories and their URLs
categories = {
    "Motherboard": "https://ddstore.mk/computercomponents/motherboards.html",
    "GPU": "https://ddstore.mk/computercomponents/graphiccards.html",
    "CPU": "https://ddstore.mk/computercomponents/processors.html",
    "Power Supply": "https://ddstore.mk/computercomponents/powersupplies.html",
    "Hard Drive": "https://ddstore.mk/computercomponents/storagedevices/internalharddrives.html",
    "Case": "https://ddstore.mk/computercomponents/pccases.html",
    "RAM": "https://ddstore.mk/computercomponents/rammemory.html",
    "Cooler": "https://ddstore.mk/computercomponents/pcfanscoolers.html"
}

all_products = []

# Function to scrape a category
def scrape_category(category, url):
    while url:
        response = scraper.get(url)

        if response.status_code != 200:
            print(f"Failed to load {category} page, status code: {response.status_code}")
            time.sleep(5)
            continue  # Retry if blocked

        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select("div.product-item-info")
        print(f"Found {len(items)} {category}s on this page.")

        for item in items:
            try:
                title_element = item.select_one("a.product-item-link")
                title = title_element.text.strip() if title_element else "No Title"
                price_element = item.select_one("span.price")
                price = price_element.text.strip() if price_element else "No Price"
                product_link = title_element["href"] if title_element else "No Link"

                all_products.append({
                    "Title": title,
                    "Price": price,
                    "Link": product_link,
                    "Category": category,
                    "Store": "DDStore"
                })
            except Exception as e:
                print(f"Error extracting {category} data: {e}")

        # Find next page button
        next_button = soup.select_one("a.action.next")
        url = next_button["href"] if next_button else None  # If no next page, stop

        time.sleep(5)  # Add delay to avoid bot detection

# Scrape both categories
for category, url in categories.items():
    scrape_category(category, url)

# Save data to CSV
df = pd.DataFrame(all_products)
df.to_csv("ddstore_products.csv", index=False, encoding="utf-8")
print("Scraping complete! Data saved to ddstore_products.csv")