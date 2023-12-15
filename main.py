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


def main():
    searchTerm = "USB fingerprint reader".replace(" ", "+")

    # Get the page
    page = get_page(f"https://www.pccasegear.com/search?query={searchTerm}&page=1")

    # Search elements for the first product and its name, price and url
    product_name_element = page.find("span", class_="product-model")
    product_price_element = page.find("div", class_="price-box").find(
        "div", class_="price"
    )
    url_element = page.find("a", class_="product-image")

    # check if the page loaded correctly by checking if the elements exist
    if not all([product_name_element, product_price_element, url_element]):
        print("The page did not load correctly.")
        with open("error_page.html", "w", encoding="utf-8") as f:
            f.write(page.prettify())
        return

    # If the page loaded correctly, extract the product name, price and url
    product_name = product_name_element.text.strip()
    product_price = product_price_element.text.strip()
    url = "https://www.pccasegear.com" + url_element["href"]

    # Print the product name, price and url
    print(f"Product Name: {product_name}")
    print(f"Price: {product_price}")
    print(f"URL: {url}")


main()
