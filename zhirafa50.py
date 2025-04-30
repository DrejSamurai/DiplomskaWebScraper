from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

browser = webdriver.Firefox()  
wait = WebDriverWait(browser, 20)

categories = {
    "Motherboard": "https://gjirafa50.mk/matichna-plocha-kompjuterski-delovi",
    "CPU": "https://gjirafa50.mk/procesor",
    "GPU": "https://gjirafa50.mk/grafichka-karta-kompjuterski-delovi",
    "Power Supply": '"https://gjirafa50.mk/izvori-na-napo%D1%98uva%D1%9Ae"',
    "Hard Drive": "https://gjirafa50.mk/disk",
    "Case": "https://gjirafa50.mk/ku%D1%9Cishte-kompjuterski-delovi",
    "RAM": "https://gjirafa50.mk/operativna-memorija-kompjuterski-delovi",
    "Cooler": "https://gjirafa50.mk/ladilnik-kompjuterski-delovi"
}

all_products = []
seen_product_links = set()  

def scrape_category(category, url):
    browser.get(url)

    while True:
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.search-result-middle.loading")))

        items = browser.find_elements(By.CSS_SELECTOR, "div.item-box")
        print(f"Found {len(items)} items in {category}.")

        for item in items:
            try:
                title = item.find_element(By.CSS_SELECTOR, "h3.product-title a").text.strip()
                product_link = item.find_element(By.CSS_SELECTOR, "h3.product-title a").get_attribute('href')

                if product_link not in seen_product_links:
                    price = item.find_element(By.CSS_SELECTOR, "span.price").text.strip()
                    img_src = item.find_element(By.CSS_SELECTOR, "section.picture img").get_attribute('data-src')

                    all_products.append({
                        "Title": title,
                        "Price": price,
                        "Link": product_link,
                        "Image": img_src,
                        "Category": category,
                        "Store": "Gjirafa50"
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