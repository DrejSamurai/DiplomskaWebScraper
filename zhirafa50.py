from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# Initialize WebDriver (no need to specify executable_path if geckodriver is in PATH)
browser = webdriver.Firefox()  # No need for executable_path if geckodriver is in PATH
wait = WebDriverWait(browser, 20)

categories = {
    "Motherboard": "https://gjirafa50.mk/matichna-plocha-kompjuterski-delovi",
    # Add other categories if needed
}

all_products = []
seen_product_links = set()  # Set to track product links we've already seen

def scrape_category(category, url):
    browser.get(url)

    while True:
        # Wait for the page to load and ensure no loading spinner is present
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.search-result-middle.loading")))

        # Scraping the product data
        items = browser.find_elements(By.CSS_SELECTOR, "div.item-box")
        print(f"Found {len(items)} items in {category}.")

        for item in items:
            try:
                title = item.find_element(By.CSS_SELECTOR, "h3.product-title a").text.strip()
                product_link = item.find_element(By.CSS_SELECTOR, "h3.product-title a").get_attribute('href')

                # Check if this product has already been seen
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

                    seen_product_links.add(product_link)  # Mark this product as seen
                else:
                    print(f"Duplicate product found: {product_link}. Skipping.")
            except Exception as e:
                print(f"Error extracting {category} data: {e}")

        # Check for the "End of Results" text
        try:
            end_of_results = browser.find_element(By.XPATH, "//span[contains(text(),'Крај на резултатите')]")
            if end_of_results.is_displayed():
                print("Reached the end of results. Exiting loop.")
                break  # Exit loop if "End of Results" is visible
        except Exception as e:
            print(f"Error checking for end of results: {e}")
        
        retries = 3
        while retries > 0:
            try:
                # Attempt to find the "Show More" button
                show_more_button = browser.find_element(By.XPATH, "//button[contains(text(),'ПОКАЖЕТЕ ПОВЕЌЕ ПРОИЗВОДИ')]")
                if show_more_button.is_displayed():
                    show_more_button.click()
                    print("Clicked 'Show More'... Loading more products...")
                    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.item-box")))  # Wait for new items to load
                    retries = 0  # Stop retrying if successful
                else:
                    print("No more 'Show More' button visible. Exiting loop.")
                    retries = 0  # Exit loop if no more "Show More" button
            except Exception as e:
                print(f"Error clicking 'Show More' button: {e}")
                retries -= 1
                if retries == 0:
                    print("Exhausted retries. Exiting loop.")

# Scrape all categories
for category, url in categories.items():
    scrape_category(category, url)

# Convert the list of scraped products into a DataFrame and save it as a CSV file
df = pd.DataFrame(all_products)
df.to_csv("gjirafa50_products.csv", index=False, encoding="utf-8")
print(f"Scraping complete! Data saved to gjirafa50_products.csv. Total products scraped: {len(all_products)}")

browser.quit()