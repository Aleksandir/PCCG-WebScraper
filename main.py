import json
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def get_page(url):
    """
    Retrieves the HTML content of a web page using Selenium and BeautifulSoup.

    Args:
        url (str): The URL of the web page to retrieve.

    Returns:
        BeautifulSoup: The parsed HTML content of the web page.
    """
    options = Options()
    options.add_argument("--headless")

    browser = webdriver.Firefox(options=options)
    browser.get(url)
    soup = BeautifulSoup(browser.page_source, "html.parser")
    browser.quit()

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


def main():
    searchTerm = "keyboard".replace(" ", "+")

    # Get the page
    page = get_page(f"https://www.pccasegear.com/search?query={searchTerm}&page=1")

    # Search elements for the first product and its name, price and url
    product_name_elements = page.findAll("span", class_="product-model")
    product_price_elements = page.findAll("div", class_="price-box")
    url_elements = page.findAll("a", class_="product-image")

    # check if the page loaded correctly by checking if the elements exist
    if not all([product_name_elements, product_price_elements, url_elements]):
        print("The page did not load correctly.")
        with open("error_page.html", "w", encoding="utf-8") as f:
            f.write(page.prettify())
        return

    # If the page loaded correctly, extract the product names, prices and urls
    # save them to a dictionary
    products = {}
    for name_element, price_element, url_element in zip(
        product_name_elements, product_price_elements, url_elements
    ):
        parsed_url = urlparse(url_element["href"])
        product_name = parsed_url.path.split("/")[-1].replace("-", " ")

        products[product_name.strip()] = {
            "price": price_element.find("div", class_="price").text,
            "url": "https://www.pccasegear.com" + url_element["href"],
        }

    # Save the data to a JSON file
    save_data(products)

    print("Done")


main()
