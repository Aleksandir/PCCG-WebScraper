import pprint

# import pandas as soup
import requests
from bs4 import BeautifulSoup

# https://quotes.toscrape.com
# https://brightdata.com/blog/how-tos/web-scraping-with-python

page = requests.get("https://quotes.toscrape.com")

if page.status_code == 200:
    print("Success!")
    soup = BeautifulSoup(page.text, "html.parser")

    # get all <h1> elements
    # on the page
    h1_elements = soup.find_all("h1")

    # get the element with id="main-title"
    main_title_element = soup.find(id="main-title")

    # find the footer element
    # based on the text it contains
    footer_element = soup.find(text={"Powered by WordPress"})

    # find the email input element
    # through its "name" attribute
    email_element = soup.find(attrs={"name": "email"})

    # find all the centered elements
    # on the page
    centered_element = soup.find_all(class_="text-center")

    # get all "li" elements
    # in the ".navbar" element
    soup.find(class_="navbar").find_all("li")

    # get all "li" elements
    # in the ".navbar" element
    soup.select(".navbar > li")


else:
    print("Failure!")
    print(page.status_code)
