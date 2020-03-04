from selenium import webdriver
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta


def expand_shadow_element(base, tags):
    for tag in tags:
        print(tag)
        element = base.find_element_by_css_selector(tag)
        base = driver.execute_script('return arguments[0].shadowRoot', element)
    return base


if __name__ == "__main__":
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = "/usr/bin/google-chrome-stable"
    driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver", options=chrome_options)

    url = "https://mijn.ing.nl/banking/service"

    driver.get(url)

    while driver.find_elements_by_xpath("/html/body/ing-app-authentication"):
        time.sleep(1)

    time.sleep(5)

    tags = [
        "dba-app",
        "ing-app-daily-banking-service",
        "ing-orange-service",
        "ing-orange-service-self-control",
    ]
    ele = expand_shadow_element(driver, tags)
    ele.find_element_by_css_selector(
        "div:nth-child(2) > .card__content > ul > li:nth-child(2) > a"
    ).click()

    time.sleep(5)

    tags = [
        "dba-download-transactions-dialog",
        "ing-orange-transaction-download-dialog",
        "ing-uic-dialog-next > section > ing-orange-transaction-download-filter",
        "ing-uic-form > form > div > div > ing-uic-date-input",
        "#viewInput",
    ]
    form = expand_shadow_element(driver, tags)
    inp = form.find_element_by_css_selector(
        "ing-uic-input-container > ing-uic-native-input > input"
    )
    inp.clear()
    inp.send_keys("01-01-2011")

    tags = [
        "dba-download-transactions-dialog",
        "ing-orange-transaction-download-dialog",
        "ing-uic-dialog-next > section > ing-orange-transaction-download-filter",
        "ing-uic-form > form > div > div > ing-uic-date-input[name='endDate']",
        "#viewInput",
    ]
    form = expand_shadow_element(driver, tags)
    inp = form.find_element_by_css_selector(
        "ing-uic-input-container > ing-uic-native-input > input"
    )
    now = datetime.now() - relativedelta(days=1)
    inp.clear()
    inp.send_keys("{}-{}-{}".format(now.day, now.month, now.year))

    tags = [
        "dba-download-transactions-dialog",
        "ing-orange-transaction-download-dialog",
        "ing-uic-dialog-next > section > ing-orange-transaction-download-filter",
    ]
    form = expand_shadow_element(driver, tags)

    form.find_element_by_css_selector(
        "ing-uic-form > form > div > ing-uic-select.format-container"
    ).click()

    time.sleep(2)

    form.find_element_by_css_selector(
        "ing-uic-form > form > div > ing-uic-select.format-container > paper-listbox > ing-uic-item[value='CSV']"
    ).click()

    time.sleep(2)

    form.find_element_by_css_selector(
        "ing-uic-form > form > paper-button[data-type='submit']"
    ).click()

    time.sleep(15)

    driver.close()
