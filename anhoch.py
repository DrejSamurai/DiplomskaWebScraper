import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import re

# List of category URLs
categories = {
    "Motherboard": "https://www.anhoch.com/categories/matichni-plochi/products?brand=&attribute=&toPrice=277990&inStockOnly=2&sort=latest&perPage=20&page=1",
    "GPU": "https://www.anhoch.com/categories/grafichki-karti/products?sort=latest&perPage=20&page=1",
    "CPU": "https://www.anhoch.com/categories/procesori/products?sort=latest&perPage=20&page=1",
    "Power Supply": "https://www.anhoch.com/categories/napojuvanja/products?sort=latest&perPage=20&page=1",
    "Hard Drive": "https://www.anhoch.com/categories/hard-disks/products?sort=latest&perPage=20&page=1",
    "Case": "https://www.anhoch.com/categories/kukji/products?sort=latest&perPage=20&page=1",
    "RAM": "https://www.anhoch.com/categories/desktop-ram-memorii/products?brand=&attribute=&toPrice=277990&inStockOnly=2&sort=latest&perPage=20&page=1",
    "Cooler": "https://www.anhoch.com/categories/ventilatori-i-ladilnici/products?brand=&attribute=&toPrice=277990&inStockOnly=2&sort=latest&perPage=20&page=1"
}

manufacturers = [
    "AMD", "Intel", "Gigabyte", "MSI", "ASUS", "ASRock", "EVGA", 
    "Zotac", "Corsair", "Cooler Master", "NZXT", "Sapphire", "PowerColor",
    "BE Quiet!", "Geil", "Crucial", "Kingston", "G.Skill", "Thermaltake", "Seasonic"
    "DeepCool", "Deepcool", "Kingston", "Grizzly"
]

def extract_manufacturer(title):
    words = title.split()

    # Case 1: If the first word is a manufacturer
    if words[0] in manufacturers:
        return words[0]

    # Case 2: If first word is a category, check the next word
    if words[0] in ["CPU", "GPU", "MB", "PSU", "DIMM"] and len(words) > 1:
        next_word = words[1]
        # Handle "BE Quiet!" which has multiple words
        if next_word == "BE" and len(words) > 2 and words[2] == "Quiet!":
            return "BE Quiet!"
        if next_word in manufacturers:
            return next_word

    # Case 3: Find manufacturer anywhere in the title
    for manu in manufacturers:
        if manu in title:
            return manu

    return "Unknown"

# Initialize WebDriver
browser = webdriver.Firefox()
wait = WebDriverWait(browser, 20)

# Store data in a list of dictionaries
all_products = []

for category, url in categories.items():
    print(f"\nScraping category: {category}")
    browser.get(url)

    while True:
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.search-result-middle.loading")))
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.search-result-middle.empty")))

        items = browser.find_elements(By.CSS_SELECTOR, "div.search-result-middle .product-card")
        print(f"Found {len(items)} items in {category}.")

        for item in items:
            title = item.find_element(By.TAG_NAME, 'h6').text.strip()
            price = item.find_element(By.CSS_SELECTOR, "div.product-card-bottom .product-price").text.strip()
            link_element = item.find_element(By.TAG_NAME, "a")
            product_link = link_element.get_attribute("href")
            image_element = item.find_element(By.CSS_SELECTOR, "a.product-image img")
            image_url = image_element.get_attribute("src")
            store = "Anhoch"

            manufacturer = extract_manufacturer(title)

            print(f"[{category}] Title: {title}")
            print(f"Manufacturer: {manufacturer}")
            print(f"Price: {price}")
            print(f"Link: {product_link}")
            print(f"Image Link:: {image_url}")
            print("-" * 50)

            # Append data to the list
            all_products.append({
                "Title": title,
                "Manufacturer": manufacturer,
                "Price": price,
                "Link": product_link,
                "Category": category,
                "Image": image_url,
                "Store": store
            })

        # Try to go to the next page
        try:
            next_button = browser.find_element(By.CSS_SELECTOR, ".pagination li:last-child button.page-link i.las.la-angle-right")
            browser.execute_script("arguments[0].click();", next_button)  
            wait.until(EC.staleness_of(items[0]))  
        except:
            print(f"Finished scraping {category}. Moving to next category...")
            break  # Exit loop if there's no next page

browser.quit()

# Convert to DataFrame and save as CSV
df = pd.DataFrame(all_products)
df.to_csv("anhoch.csv", index=False, encoding="utf-8")

print("\n✅ Data saved to 'anhoch.csv' successfully!")