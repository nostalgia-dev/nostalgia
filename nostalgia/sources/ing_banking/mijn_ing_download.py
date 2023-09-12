from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta


def get_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = "/usr/bin/google-chrome-stable"
    driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver", options=chrome_options)
    return driver


def scrape_ing():
    driver = get_driver()
    driver.get("https://mijn.ing.nl/banking/service?dialog=download-transactions")

    while driver.find_elements_by_xpath("/html/body/ing-app-authentication-router"):
        print("Waiting for user to login in browser... (don't forget to confirm using 2FA)")
        time.sleep(2)

    print("Logged in")

    time.sleep(5)

    roots = {
        x: driver.execute_script("return arguments[0].shadowRoot", x) for x in driver.find_elements_by_xpath("//*")
    }
    root_eles = [k for k, v in roots.items() if v]

    for x in root_eles:
        if "download-transaction-loader" not in x.tag_name:
            continue
        tag_value = int(x.tag_name.split("-")[-1])
        shadow_root_dict = driver.execute_script("return arguments[0].shadowRoot", x)
        shadow_root = WebElement(driver, list(shadow_root_dict.values())[0], w3c=True)
        shadow_content = shadow_root.find_element_by_css_selector(f"download-transaction-{tag_value+1}")

    shadow_root_dict = driver.execute_script("return arguments[0].shadowRoot", shadow_content)
    shadow_root = WebElement(driver, list(shadow_root_dict.values())[0], w3c=True)
    shadow_content = shadow_root.find_element_by_css_selector(f"ing-form-{tag_value+2}")

    inp = shadow_content.find_element_by_xpath(".//*[@id = 'date-from-picker']/input")
    inp.clear()
    inp.send_keys(f"01-01-{datetime.now().year-8}")

    shadow_content.find_element_by_xpath(".//*[@id = 'file-types-drop-down']/select/option[3]").click()

    shadow_content.find_element_by_xpath(".//*[@data-tag-name = 'ing-button']").click()

    time.sleep(60)

    driver.close()


# def expand_shadow_element(base, tags):
#     for tag in tags:
#         print(tag)
#         element = base.find_elements("css selector", tag)[0]
#         base = driver.execute_script("return arguments[0].shadowRoot", element)
#         if isinstance(base, dict):
#             base = WebElement(driver, base, w3c=True)
#     return base
