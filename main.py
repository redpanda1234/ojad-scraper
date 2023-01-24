from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import genanki


def init_browser():
    firefox_dev_binary = FirefoxBinary("/usr/bin/firefox-developer-edition")

    fp = webdriver.FirefoxProfile()

    options = Options()
    options.add_argument("--headless")

    browser = webdriver.Firefox(
        firefox_binary=firefox_dev_binary,
        executable_path="./geckodriver",
        firefox_profile=fp,
        options=options,
    )

    return browser


def get_ojad_page(browser):
    base_url = "https://www.gavo.t.u-tokyo.ac.jp/ojad/phrasing/index"
    page = browser.get(base_url)
    return browser


def open_ojad():
    browser = init_browser()
    browser = get_ojad_page(browser)
    return browser


def wait_for_element(browser, By_what, trigger_string, kanji_string, timeout=5):
    try:
        element_loaded = EC.presence_of_element_located((By_what, trigger_string))
        WebDriverWait(browser, timeout).until(element_loaded)

    except TimeoutException:
        print(f"Timed out on word {kanji_string}")


def query_ojad(browser, kanji_string, timeout=5):
    # wait for text box to appear and then enter our kanji string into it
    wait_for_element(browser, By.ID, "PhrasingText", kanji_string, timeout=timeout)
    browser.execute_script(
        "document.getElementById('PhrasingText').innerHTML = '" + kanji_string + " ';"
    )

    # request pitch analysis
    wait_for_element(
        browser, By.ID, "phrasing_submit_wrapper", kanji_string, timeout=timeout
    )
    browser.find_element(By.ID, "phrasing_submit_wrapper").click()

    # wait for result to appear
    wait_for_element(
        browser, By.CLASS_NAME, "phrasing_phrase_wrapper", kanji_string, timeout=timeout
    )

    pitch_curve_data = browser.find_element(By.CLASS_NAME, "phrasing_phrase_wrapper")

    return pitch_curve_data


def process_words(browser, wordlist, timeout=5):
    word_dict = {}
    for word in wordlist:
        word_data = query_ojad(browser, word, timeout=timeout)
        # word_data.screenshot("/tmp/" + word + ".png")
        word_dict[word] = word_data.get_attribute("outerHTML")
    return word_dict


def test():
    browser = open_ojad()
    words = ["ために", "入学試験", "一生けんめい", "将来"]
    word_dict = process_words(browser, words)


def gen_cards():
    shit_deck = genanki
