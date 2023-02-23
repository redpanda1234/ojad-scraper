from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def init_browser(mode="default"):
    """
    initialize a selenium browser to query websites

    Creates a browser with different possible options
    Default option is hard configured for a particular setup
    """
    options = Options()
    if mode == "default":
        # default version
        options.add_argument("--headless")
        firefox_dev_binary = FirefoxBinary("/usr/bin/firefox-developer-edition")
        fp = webdriver.FirefoxProfile()
        browser = webdriver.Firefox(
            firefox_binary=firefox_dev_binary,
            executable_path="./geckodriver",
            firefox_profile=fp,
            options=options,
        )
    elif mode == "standard":
        options.add_argument("--headless")
        browser = webdriver.Firefox(
            options=options,
        )
    elif mode == "headed":
        browser = webdriver.Firefox(
            options=options,
        )
        
    return browser

def wait_for_element(browser, By_what, trigger_string, kanji_string, timeout=10):
    try:
        element_loaded = EC.presence_of_element_located((By_what, trigger_string))
        WebDriverWait(browser, timeout).until(element_loaded)

    except TimeoutException:
        print(f"Timed out on word {kanji_string}")
