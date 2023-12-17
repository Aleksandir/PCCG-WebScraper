from main import get_page

# scrape ul tag
# scrape inner ul tag
# scrape li tag for product url
# if li tag has ul tag, recurse to get product url and not the category page as the info wont be present
# stop at end of ul tag
# save product url to list
# once list is complete, save to sources.txt file with a link on each line


def get_product_urls(url):
    """
    Gets the product URLs from a category page.

    Args:
        url (str): The URL of the category page.

    Returns:
        list: A list of product URLs.
    """

    page = get_page(url)

    product_urls = []
    product_url_elements = page.findAll("li")

    for product_url_element in product_url_elements:
        link = product_url_element.find("a")
        url = link["href"]
        if (
            url.startswith("https://www.pccasegear.com/category/")
            and url not in product_urls
        ):
            product_urls.append(url)

    return product_urls


def main():
    SITEMAP_URL = "https://www.pccasegear.com/site_map"
    product_urls = get_product_urls(SITEMAP_URL)

    with open("src/sources.txt", "w") as f:
        for product_url in product_urls:
            f.write(f"{product_url}\n")


if __name__ == "__main__":
    main()
