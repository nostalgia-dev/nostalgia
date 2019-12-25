import getpass
from selenium import webdriver
from nostalgia.utils import MockCredentials


def get_driver(
    executable_path="chromedriver",
    binary_location=None,
    headless=False,
    credentials=None,
    login_url=None,
    user_xpath_or_id="username",
    password_xpath_or_id="password",
    **options,
):
    # set options
    chrome_options = webdriver.ChromeOptions()
    if headless:
        chrome_options.add_argument('headless')
    if binary_location is not None:
        setattr(chrome_options, "binary_location", binary_location)
    for k, v in options.items():
        setattr(chrome_options, k, v)
    driver = webdriver.Chrome(executable_path=executable_path, options=chrome_options)

    # login if neccessary
    if isinstance(credentials, dict):
        credentials = MockCredentials(credentials)
    if credentials is not None:
        driver.get(login_url)
        if user_xpath_or_id.startswith("/"):
            user_element = driver.find_elements_by_xpath(user_xpath_or_id)[0]
        else:
            user_element = driver.find_element_by_id(user_xpath_or_id)
        if password_xpath_or_id.startswith("/"):
            password_element = driver.find_elements_by_xpath(password_xpath_or_id)[0]
        else:
            password_element = driver.find_element_by_id(password_xpath_or_id)
        user_element.send_keys(credentials.username)
        password = credentials.password
        password_element.send_keys(password)  # h
        password_element.submit()

    return driver
