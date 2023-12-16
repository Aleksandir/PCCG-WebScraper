import json
import sys

# TODO Could look at using concurrent.futures to speed up the scraping process, currently seems fast enough
# from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

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


#! This function is not complete
#! once search page circles back to the first page, it will not stop loading
# The page did not load correctly. Skipping...
# The page did not load correctly. Skipping...
# The page did not load correctly. Skipping...
def scrape_search_page(searchTerm):
    """
    Scrapes the search page of a website to retrieve product information.

    Args:
        searchTerm (str): The search term used to query the website.

    Returns:
        dict: A dictionary containing the product names as keys and their corresponding prices and URLs as values.
    """
    # Get the page
    page_number = 1
    products = {}
    while True:
        page = get_page(
            f"https://www.pccasegear.com/search?query={searchTerm}&page={page_number}"
        )
        try:
            page_viewing = int(
                page.find(
                    "a", class_="ais-Pagination-link ais-Pagination-link--selected"
                ).text
            )
        except AttributeError:
            if page_number == 1:
                print("No results found.")
            else:
                print("The page did not load correctly. Skipping...")
                page_number += 1
                continue

        # test if the current page is the page we are viewing
        # otherwise we have reached the end of the search results
        if page_viewing == page_number:
            print(f"Page {page_number} loaded.")
        else:
            break

        # Search elements for the first product and its name, price and url
        product_name_elements = page.findAll("span", class_="product-model")
        product_price_elements = page.findAll("div", class_="price-box")
        url_elements = page.findAll("a", class_="product-image")

        # check if the page loaded correctly by checking if the elements exist
        if not all([product_name_elements, product_price_elements, url_elements]):
            print("The page did not load correctly.")
            with open("error_page.html", "w", encoding="utf-8") as f:
                f.write(page.prettify())
            break

        # If the page loaded correctly, extract the product names, prices and urls
        # save them to a dictionary
        for name_element, price_element, url_element in zip(
            product_name_elements, product_price_elements, url_elements
        ):
            parsed_url = urlparse(url_element["href"])
            product_name = parsed_url.path.split("/")[-1].replace("-", " ")

            # If the product name is empty, skip it
            if product_name.strip() == "":
                continue
            else:
                products[product_name.strip()] = {
                    "price": price_element.find("div", class_="price").text,
                    "url": "https://www.pccasegear.com" + url_element["href"],
                }

        # Increment page number
        page_number += 1

    return products


def main():
    save_count = 0
    SOURCES_FILE = "src/sources.txt"
    print("Scraping PCCaseGear...")

    search_terms = get_search_pages(SOURCES_FILE)

    for term in search_terms:
        if term.startswith("https://"):
            print(f"Scraping {term.split("/")[-1].replace("-", " ").strip()}...")
            products = scrape_product_category_page(term)
            save_data(products)
            print(f"{len(products)} products saved")
            save_count += len(products)
        else:
            #! This is not complete and will not work
            print(f"Searching for {term}...")
            products = scrape_search_page(term)

    print(f"\n{save_count} products scraped and saved in total.")

    # browser.quit()
    sys.exit()


if __name__ == "__main__":
    main()
