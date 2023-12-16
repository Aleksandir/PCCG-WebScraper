import concurrent.futures
import json
import sys
import threading

# TODO Could look at using concurrent.futures to speed up the scraping process, currently seems fast enough
# from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from tqdm import tqdm

options = Options()
options.add_argument("--headless")
browser = webdriver.Firefox(options=options)


def get_search_pages(file):
    with open(file, "r") as f:
        search_terms = f.readlines()

    return search_terms


def get_page(url):
    """
    Retrieves the HTML content of a web page using Selenium and BeautifulSoup.

    Args:
        url (str): The URL of the web page to retrieve.

    Returns:
        BeautifulSoup: The parsed HTML content of the web page.
    """
    browser.get(url)
    soup = BeautifulSoup(browser.page_source, "html.parser")

    return soup


def save_data(data):
    """
    Save the given data to a JSON file.

    Parameters:
    data (dict): The data to be saved.

    Returns:
    None
    """
    # Load existing data

    try:
        with open("products.json", "r") as f:
            existing_data = json.load(f)
    except json.JSONDecodeError:
        existing_data = {}
    except FileNotFoundError:
        existing_data = {}

    # Update data
    updated = False
    for key, value in data.items():
        if key not in existing_data:
            existing_data[key] = value

        elif existing_data[key] != value:
            print("**Updates**") if not updated else None
            updated = True
            print(
                f"\nKey: {key}\n- Old Value: {existing_data[key]}\n- New Value: {value}\n"
            )
            existing_data[key] = value

    # Write data back to file
    with open("products.json", "w") as f:
        json.dump(existing_data, f, indent=2)


def scrape_product_category_page(url):
    """
    Scrapes a product category page and returns a dictionary of products.

    Args:
        url (str): The URL of the product category page.

    Returns:
        dict: A dictionary containing the product names, prices, and URLs.
    """
    page = get_page(url)
    products = {}
    product_name_elements = page.findAll("a", class_="product-title")
    product_price_elements = page.findAll("div", class_="price-box")

    for i in range(len(product_name_elements)):
        product_name = product_name_elements[i].text
        products[product_name.strip()] = {
            "price": product_price_elements[i].find("div", class_="price").text,
            "url": product_name_elements[i]["href"],
        }

    return products


print_lock = threading.Lock()


def scrape_and_save(url):
    products = scrape_product_category_page(url)
    return products


def main():
    SOURCES_FILE = "src/sources.txt"
    print("Scraping PCCaseGear...")

    site_urls = get_search_pages(SOURCES_FILE)

    all_products = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_url = {
            executor.submit(scrape_and_save, url): url for url in site_urls
        }

        for future in tqdm(
            concurrent.futures.as_completed(future_to_url),
            total=len(future_to_url),
            desc="Scraping progress",
        ):
            url = future_to_url[future]
            try:
                data = future.result()
            except Exception as exc:
                print("%r generated an exception: %s" % (url, exc))
            else:
                all_products.update(data)

    save_data(all_products)
    print(f"\n{len(all_products)} products scraped and saved in total.")
    browser.quit()
    sys.exit()


if __name__ == "__main__":
    main()
