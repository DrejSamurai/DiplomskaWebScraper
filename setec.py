import cloudscraper
import time
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin

scraper = cloudscraper.create_scraper()

categories = {
    "Motherboard": "https://setec.mk/computers--it/pc-and-pc-equipment/motherboard",
    # "CPU": "https://setec.mk/computers--it/pc-and-pc-equipment/processor",
    # "GPU": "https://setec.mk/computers--it/pc-and-pc-equipment/graphic-cards",
    # "Power Supply": "https://setec.mk/computers--it/pc-and-pc-equipment/power-supply",
    # "Hard Drive": "https://setec.mk/computers--it/pc-and-pc-equipment/hard-disks",
    # "Case": "https://setec.mk/computers--it/pc-and-pc-equipment/case",
    # "RAM": "https://setec.mk/computers--it/pc-and-pc-equipment/ram-memory",
    # "Cooler": "https://setec.mk/computers--it/pc-and-pc-equipment/coolers"
}

all_products = []
manufacturers = [
    "AMD", "Intel", "Gigabyte", "MSI", "ASUS", "ASRock", "EVGA", 
    "Zotac", "Corsair", "Cooler Master", "NZXT", "Sapphire", "PowerColor",
    "BE Quiet!", "Geil", "Crucial", "Kingston", "G.Skill", "Thermaltake", "Seasonic"
    "DeepCool", "Deepcool", "Kingston", "Grizzly", "ASROCK"
]

def standardize_price(price_str):
    price_str = price_str.replace("ден", "").strip()
    price_str = price_str.replace(".", "").replace(",", ".")
    try:
        return int(float(price_str))
    except ValueError:
        return 0


def extract_manufacturer(title):
    words = title.split()

    if words[0] in manufacturers:
        return words[0]

    if words[0] in ["CPU", "GPU", "MB", "PSU", "DIMM"] and len(words) > 1:
        next_word = words[1]
        if next_word == "BE" and len(words) > 2 and words[2] == "Quiet!":
            return "BE Quiet!"
        if next_word in manufacturers:
            return next_word

    for manu in manufacturers:
        if manu in title:
            return manu

    return " "
    

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
                title = title_element.text.strip() if title_element else " "
                product_link = urljoin(base_url, title_element["href"]) if title_element else " "
                
                price_element = item.select_one("span.price-new-new")
                raw_price = price_element.text.strip() if price_element else " "
                price = standardize_price(raw_price)
                manufacturer = extract_manufacturer(title)

                all_products.append({
                    "Title": title,
                    "Manufacturer": manufacturer,
                    "Price": price,
                    "Code": " ",
                    "Warranty": " ",
                    "Link": product_link,
                    "Category": category,
                    "Description": " ",
                    "Image": " ",
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