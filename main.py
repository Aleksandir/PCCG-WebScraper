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

else:
    print("Failure!")
    print(page.status_code)
