from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

browser = webdriver.Firefox()  
wait = WebDriverWait(browser, 20)

categories = {
    "Motherboard": "https://gjirafa50.mk/matichna-plocha-kompjuterski-delovi",
    # "CPU": "https://gjirafa50.mk/procesor",
    # "GPU": "https://gjirafa50.mk/grafichka-karta-kompjuterski-delovi",
    # "Power Supply": '"https://gjirafa50.mk/izvori-na-napo%D1%98uva%D1%9Ae"',
    # "Hard Drive": "https://gjirafa50.mk/disk",
    # "Case": "https://gjirafa50.mk/ku%D1%9Cishte-kompjuterski-delovi",
    # "RAM": "https://gjirafa50.mk/operativna-memorija-kompjuterski-delovi",
    # "Cooler": "https://gjirafa50.mk/ladilnik-kompjuterski-delovi"
}

all_products = []
manufacturers = [
    "AMD", "Intel", "Gigabyte", "MSI", "ASUS", "ASRock", "EVGA", 
    "Zotac", "Corsair", "Cooler Master", "NZXT", "Sapphire", "PowerColor",
    "BE Quiet!", "Geil", "Crucial", "Kingston", "G.Skill", "Thermaltake", "Seasonic"
    "DeepCool", "Deepcool", "Kingston", "Grizzly", "ASROCK"
]

def standardize_price(price_str):
    price_str = price_str.replace("MKD", "").replace("ден", "").replace(".", "").replace(",", "").strip()
    price_str = ''.join(filter(str.isdigit, price_str))
    try:
        return int(price_str)
    except ValueError:
        return 0

def standardize_title(title):
    if title.startswith("Pllakë amë"):
        return title.replace("Pllakë amë", "", 1).strip()
    elif title.startswith("Матична плоча"):
        return title.replace("Матична плоча", "", 1).strip()
    return title

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


seen_product_links = set()  

def scrape_category(category, url):
    browser.get(url)

    while True:
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.search-result-middle.loading")))

        items = browser.find_elements(By.CSS_SELECTOR, "div.item-box")
        print(f"Found {len(items)} items in {category}.")

        for item in items:
            try:
                raw_title = item.find_element(By.CSS_SELECTOR, "h3.product-title a").text.strip()
                title = standardize_title(raw_title)
                product_link = item.find_element(By.CSS_SELECTOR, "h3.product-title a").get_attribute('href')

                if product_link not in seen_product_links:
                    raw_price = item.find_element(By.CSS_SELECTOR, "span.price").text.strip()
                    price = standardize_price(raw_price)
                    manufacturer = extract_manufacturer(title)
                    img_element = item.find_element(By.CSS_SELECTOR, "section.picture img")
                    img_src = img_element.get_attribute('data-src') or img_element.get_attribute('src')

                    all_products.append({
                    "Title": title,
                    "Manufacturer": manufacturer,
                    "Price": price,
                    "Code": " ",
                    "Warranty": " ",
                    "Link": product_link,
                    "Category": category,
                    "Description": " ",
                    "Image": img_src,
                    "Store": "Zhirafa50"
                    })

                    seen_product_links.add(product_link)  
                else:
                    print(f"Duplicate product found: {product_link}. Skipping.")
            except Exception as e:
                print(f"Error extracting {category} data: {e}")

        try:
            end_of_results = browser.find_element(By.XPATH, "//span[contains(text(),'Крај на резултатите')]")
            if end_of_results.is_displayed():
                print("Reached the end of results. Exiting loop.")
                break  
        except Exception as e:
            print(f"Error checking for end of results: {e}")
        
        retries = 3
        while retries > 0:
            try:
                show_more_button = browser.find_element(By.XPATH, "//button[contains(text(),'ПОКАЖЕТЕ ПОВЕЌЕ ПРОИЗВОДИ')]")
                if show_more_button.is_displayed():
                    show_more_button.click()
                    print("Clicked 'Show More'... Loading more products...")
                    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.item-box")))  
                    retries = 0 
                else:
                    print("No more 'Show More' button visible. Exiting loop.")
                    retries = 0  
            except Exception as e:
                print(f"Error clicking 'Show More' button: {e}")
                retries -= 1
                if retries == 0:
                    print("Exhausted retries. Exiting loop.")

for category, url in categories.items():
    scrape_category(category, url)

df = pd.DataFrame(all_products)
df.to_csv("gjirafa50_products.csv", index=False, encoding="utf-8")
print(f"Scraping complete! Data saved to gjirafa50_products.csv. Total products scraped: {len(all_products)}")

browser.quit()