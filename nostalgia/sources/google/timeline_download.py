import time
import os
import shutil
from selenium import webdriver
from calendar import monthrange
from datetime import datetime
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotVisibleException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
)

SELENIUM_EXCEPTIONS = (
    NoSuchElementException,
    ElementNotVisibleException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
)

BASE_PATH = os.path.expanduser("~/Downloads")

# chrome_options = webdriver.ChromeOptions()
# chrome_options.binary_location = "/usr/bin/google-chrome-stable"


def move(fname):
    src = os.path.join(BASE_PATH, fname)
    try:
        shutil.move(src, os.path.join(BASE_PATH, "ghistory", fname))
    except FileNotFoundError:
        print("ERROR: file not found", src)


def exists(year, month, day):
    fname = "history-{}-{:02d}-{:02d}.kml".format(year, month, day)
    return os.path.exists(os.path.join(BASE_PATH, "ghistory", fname))


def get_last_day_of_month(year, num_month):
    return monthrange(year, num_month)[1]


def select_year(year):
    driver.find_element_by_class_name("year-picker").click()
    time.sleep(0.3)
    for ele in driver.find_elements_by_xpath("//div[text() = '{}']/parent::*".format(year)):
        try:
            ele.click()
            break
        except SELENIUM_EXCEPTIONS:
            pass
    time.sleep(1)


def select_month(month):
    driver.find_element_by_class_name("month-picker").click()
    time.sleep(0.3)
    for ele in driver.find_elements_by_xpath("//div[text() = '{}']/parent::*".format(month)):
        try:
            ele.click()
            break
        except SELENIUM_EXCEPTIONS:
            pass
    time.sleep(1)


def click_download():
    driver.find_element_by_xpath("//div[@aria-label=' Settings ']").click()
    time.sleep(1)
    for ele in driver.find_elements_by_xpath("//div[text() = 'Export this day to KML']/parent::*"):
        try:
            ele.click()
            break
        except SELENIUM_EXCEPTIONS:
            pass
    time.sleep(1)


MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

if __name__ == "__main__":
    driver = webdriver.Chrome()  # , options=chrome_options

    url = "https://www.google.com/maps/timeline?pb=!1m2!1m1!1s2019-02-29"

    driver.get(url)

    now = datetime.now()
    today = (now.year, now.month, now.day)

    # wait for being logged in
    while not driver.find_elements_by_xpath(
        "//span[@class='header-feature-name' and text() = ' Timeline ']"
    ):
        time.sleep(2)

    time.sleep(5)

    try:
        last_clicked_year = None
        last_clicked_month = None
        for year in range(now.year, 2014, -1):
            for num_month, month in enumerate(MONTHS[::-1]):
                num_month = 12 - num_month
                for day in range(get_last_day_of_month(year, num_month), 0, -1):
                    date_tuple = (year, num_month, day)
                    if date_tuple >= today:
                        continue
                    if exists(year, num_month, day):
                        continue
                    print(num_month, date_tuple)
                    # select year if neccessary
                    if last_clicked_year != year:
                        select_year(year)
                        last_clicked_year = year
                    # select month if neccessary
                    if last_clicked_month != month:
                        select_month(month)
                        last_clicked_month = month
                    # handle day
                    driver.find_element_by_class_name("day-picker").click()

                    driver.find_element_by_xpath(
                        "//td[@aria-label='{} {}']".format(day, month[:3])
                    ).click()

                    time.sleep(3)

                    click_download()

                    time.sleep(3)

                    fname = "history-{}-{:02d}-{:02d}.kml".format(year, num_month, day)

                    move(fname)
    finally:
        driver.quit()

    from nostalgia.sources.google.timeline_transform import *
    from nostalgia.sources.google.timeline import *
