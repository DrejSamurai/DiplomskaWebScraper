import cloudscraper
import time
import pandas as pd
from bs4 import BeautifulSoup

scraper = cloudscraper.create_scraper()

categories = {
    "Motherboard": "https://ddstore.mk/computercomponents/motherboards.html",
    # "GPU": "https://ddstore.mk/computercomponents/graphiccards.html",
    # "CPU": "https://ddstore.mk/computercomponents/processors.html",
    # "Power Supply": "https://ddstore.mk/computercomponents/powersupplies.html",
    # "Hard Drive": "https://ddstore.mk/computercomponents/storagedevices/internalharddrives.html",
    # "Case": "https://ddstore.mk/computercomponents/pccases.html",
    # "RAM": "https://ddstore.mk/computercomponents/rammemory.html",
    # "Cooler": "https://ddstore.mk/computercomponents/pcfanscoolers.html"
}

all_products = []
manufacturers = [
    "AMD", "Intel", "Gigabyte", "MSI", "ASUS", "ASRock", "EVGA", 
    "Zotac", "Corsair", "Cooler Master", "NZXT", "Sapphire", "PowerColor",
    "BE Quiet!", "Geil", "Crucial", "Kingston", "G.Skill", "Thermaltake", "Seasonic"
    "DeepCool", "Deepcool", "Kingston", "Grizzly"
]

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
    while url:
        response = scraper.get(url)

        if response.status_code != 200:
            print(f"Failed to load {category} page, status code: {response.status_code}")
            time.sleep(5)
            continue  

        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select("div.product-item-info")
        print(f"Found {len(items)} {category}s on this page.")

        for item in items:
            try:
                title_element = item.select_one("a.product-item-link")
                title = title_element.text.strip() if title_element else " "
                price_element = item.select_one("span.price")
                price = price_element.text.strip() if price_element else " "
                product_link = title_element["href"] if title_element else " "
                image_element = item.select_one(".product-image-photo")
                image_link = image_element["src"] if image_element and "src" in image_element.attrs else " "
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
                    "Image": image_link,
                    "Store": "DDStore"
                })
            except Exception as e:
                print(f"Error extracting {category} data: {e}")

        next_button = soup.select_one("a.action.next")
        url = next_button["href"] if next_button else None  

        time.sleep(5)  

for category, url in categories.items():
    scrape_category(category, url)

df = pd.DataFrame(all_products)
df.to_csv("ddstore_products.csv", index=False, encoding="utf-8")
print("Scraping complete! Data saved to ddstore_products.csv")