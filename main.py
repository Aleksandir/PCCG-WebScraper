import pprint

import requests
from bs4 import BeautifulSoup


def main():
    searchTerm = input("Enter the product you would like to search for: ").strip()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    page = requests.get(
        f"https://www.woolworths.com.au/shop/search/products?searchTerm={searchTerm}&pageNumber=1&sortBy=CUPAsc",
        headers=headers,
    )

    if page.status_code == 200:
        print("Success!")
        soup = BeautifulSoup(page.content, "html.parser")

        # Check if the page loaded correctly
        product_name_element = soup.find("div", class_="title")
        product_price_element = soup.find("div", class_="primary")
        if product_name_element is None or product_price_element is None:
            print("The page did not load correctly.")
            with open("error_page.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())
            return

        # If the page loaded correctly, extract the product name and price
        product_name = product_name_element.text.strip()
        product_price = product_price_element.text.strip()

        print(f"Product Name: {product_name}")
        print(f"Price: {product_price}")
    else:
        match page.status_code:
            case 403:
                print("Access denied!")
            case 404:
                print("Page not found!")
            case 500:
                print("Server error!")
            case _:
                print("Failure!")
                print(page.status_code)


main()
