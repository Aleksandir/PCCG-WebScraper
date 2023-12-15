import json
import sys

# from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

options = Options()
options.add_argument("--headless")
browser = webdriver.Firefox(options=options)


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
        json.dump(existing_data, f)


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


def scrape_search_page(searchTerm):
    """
    Scrapes the search page of a website to retrieve product information.

    Args:
        searchTerm (str): The search term used to query the website.

    Returns:
        dict: A dictionary containing the product names, prices, and URLs.
    """
    # Rest of the code...


def scrape_search_page(searchTerm):
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
                sys.exit()
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
    print("Scraping PCCaseGear...")
    print("1. Search for a product")
    print("2. Scrape a product category")
    choice = input("Enter your choice: ")
    while choice not in ["1", "2"]:
        choice = input("Enter your choice: ")

    if choice == "1":
        category = input("Enter the product category: ")
        products = scrape_search_page(category)
    elif choice == "2":
        url = input("Enter the URL of the product category: ")
        products = scrape_product_category_page(url)

    # Save the data
    save_data(products)
    print(f"{len(products)} products saved to products.json")
    browser.quit()


main()
