from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service


def get_page(url):
    options = Options()
    options.add_argument("--headless")

    browser = webdriver.Firefox(options=options)
    browser.get(url)
    soup = BeautifulSoup(browser.page_source, "html.parser")
    browser.quit()

    return soup


def main():
    # searchTerm = input("Enter the product you would like to search for: ").strip()
    searchTerm = "USB fingerprint reader"
    for char in searchTerm:
        if char == " ":
            searchTerm = searchTerm.replace(" ", "+")

    # Get the page
    page = get_page(f"https://www.pccasegear.com/search?query={searchTerm}&page=1")

    # Check if the page loaded correctly
    product_name_element = page.find("span", class_="product-model")
    product_price_element = page.find("div", {"class": "price-box"}).find(
        "div", {"class": "price"}
    )
    # pull the url for the product
    url = page.find("a", class_="product-image")
    url = "https://www.pccasegear.com" + url["href"]
    if product_name_element is None or product_price_element is None:
        print("The page did not load correctly.")
        with open("error_page.html", "w", encoding="utf-8") as f:
            f.write(page.prettify())
        return

    # If the page loaded correctly, extract the product name and price
    product_name = product_name_element.text.strip()
    product_price = product_price_element.text.strip()

    print(f"Product Name: {product_name}")
    print(f"Price: {product_price}")
    print(f"URL: {url}")


main()
