# import getpass
# from nostalgia.selenium import get_driver
# import lxml.html

# driver = get_driver(
#     credentials={"username": "kootenpv@gmail.com", "password": getpass.getpass()},
#     login_url="https://www.ah.nl/mijn/inloggen",
# )

# url = "https://www.ah.nl/producten/eerder-gekocht?sorting=last_bought"

# driver.get(url)

# tree = lxml.html.fromstring(driver.page_source)

# prices = [x.text_content() for x in tree.xpath("//div[@class='product-price']")]
# descriptions = [
#     x.text_content().replace("\xad", "")
#     for x in tree.xpath("//div[@class='product-description']/h1")
# ]
# links = [
#     "https://www.ah.nl" + x for x in tree.xpath("//article[contains(@class, 'product')]/a/@href")
# ]
