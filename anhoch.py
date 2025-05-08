import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import re
import numpy as np
import math

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

def standardize_price(price_str):
    price_str = price_str.replace("ден", "").strip()
    price_str = price_str.replace(".", "").replace(",", ".")
    try:
        return int(float(price_str))
    except ValueError:
        return 0

def get_product_details(browser, url):
    original_window = browser.current_window_handle
    browser.execute_script("window.open(arguments[0], '_blank');", url)
    WebDriverWait(browser, 10).until(EC.number_of_windows_to_be(2))
    new_window = [w for w in browser.window_handles if w != original_window][0]
    browser.switch_to.window(new_window)

    code = " "
    warranty = " "
    description = " "

    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".additional-info"))
        )
        info_items = browser.find_elements(By.CSS_SELECTOR, ".additional-info li")

        for item in info_items:
            try:
                label = item.find_element(By.TAG_NAME, "label").text.strip()
                if "Шифра" in label:
                    code_text = item.get_attribute("innerText").replace("Шифра:", "").strip()
                    code = code_text
                elif "Гаранција" in label:
                    warranty_text = item.find_element(By.CLASS_NAME, "sku").text.strip()
                    warranty_match = re.search(r'\d+', warranty_text)
                    if warranty_match:
                        warranty = int(warranty_match.group())//12
            except Exception:
                continue

        try:
            desc_elem = browser.find_element(By.ID, "description")
            description = desc_elem.text.strip()
        except Exception:
            description = " "

    except Exception as e:
        print(f"Error loading details from {url}: {e}")

    browser.close()
    browser.switch_to.window(original_window)
    return code, warranty, description

browser = webdriver.Firefox()
wait = WebDriverWait(browser, 20)
all_products = []

for category, url in categories.items():
    browser.get(url)

    while True:
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.search-result-middle.loading")))
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.search-result-middle.empty")))

        items = browser.find_elements(By.CSS_SELECTOR, "div.search-result-middle .product-card")

        for item in items:
            title = item.find_element(By.TAG_NAME, 'h6').text.strip()
            raw_price = item.find_element(By.CSS_SELECTOR, "div.product-card-bottom .product-price").text.strip()
            price = standardize_price(raw_price)
            link_element = item.find_element(By.TAG_NAME, "a")
            product_link = link_element.get_attribute("href")
            image_element = item.find_element(By.CSS_SELECTOR, "a.product-image img")
            image_url = image_element.get_attribute("src")
            store = "Anhoch"

            manufacturer = extract_manufacturer(title)
            code, warranty, description = get_product_details(browser, product_link)

            all_products.append({
                "Title": title,
                "Manufacturer": manufacturer,
                "Price": price,
                "Code": code,
                "Warranty": warranty,
                "Link": product_link,
                "Category": category,
                "Description": description,
                "Image": image_url,
                "Store": store
            })       
        try:
            next_button = browser.find_element(By.CSS_SELECTOR, ".pagination li:last-child button.page-link i.las.la-angle-right")
            browser.execute_script("arguments[0].click();", next_button)  
            wait.until(EC.staleness_of(items[0]))  
        except:
            print(f"Finished scraping {category}. Moving to next category...")
            break  

browser.quit()

df = pd.DataFrame(all_products)
df.to_csv("anhoch.csv", index=False, encoding="utf-8")

print("\n✅ Data saved to 'anhoch.csv' successfully!")