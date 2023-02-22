from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from tqdm import tqdm as tqdm

from time import sleep
import random
import re


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
    browser.get(base_url)
    return browser


def open_ojad():
    browser = init_browser()
    browser = get_ojad_page(browser)
    return browser


def wait_for_element(browser, By_what, trigger_string, kanji_string, timeout=15):
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


# def process_words(browser, words, timeout=5):
#     word_dict = {}
#     for word in tqdm(words):
#         word_data = query_ojad(browser, word, timeout=timeout)
#         # word_data.screenshot("/tmp/" + word + ".png")
#         word_dict[word] = word_data.get_attribute("outerHTML")
#         sleep(2 * random.uniform(0, 1))  # Not sure if they'll like ban
#         # me or something if I query their website too much
#     return word_dict
def extract_kana_string(ojad_html):
    between_html_tags = [char for char in re.findall(r">(.*?)<", ojad_html)]
    output_str = "".join([char for char in between_html_tags if char.replace(" ", "")])
    assert "<" not in output_str and ">" not in output_str
    return output_str


def check_reading_matches(pitch_reading, true_kana):
    """
    true_kana should be extracted from the vocabulary csv file or
    something like that
    """
    ojad_kana = extract_kana_string(pitch_reading)

    # 少し input sanitize します
    # For some reason I think there might be two different wave
    # dashes??
    for to_strip in "〜～()":
        true_kana = true_kana.replace(to_strip, "")

    if ojad_kana != true_kana:
        print(
            f"OJAD derives incorrect reading for {true_kana}. Got {ojad_kana} instead."
        )
        return False
    return True


def get_words_pitch(browser, words, timeout=5):
    """
    This one expects "words" to be a collection of tuples of the form
    (kana, kanji, english, lesson)
    """
    word_dict = {}
    for word in tqdm(words):
        kana, kanji, english, lesson = word
        if kanji:
            word_data = query_ojad(browser, kanji, timeout=timeout)
        elif kana:
            word_data = query_ojad(browser, kana, timeout=timeout)
        else:
            print(word)
            assert False

        pitch_reading = word_data.find_element(
            By.CLASS_NAME, "phrasing_text"
        ).get_attribute("outerHTML")

        matched = check_reading_matches(pitch_reading, kana)
        # Default to using kana in case where kanji reading didn't
        # yield the expected result
        if not matched and kanji:
            print(f"Kanji: {kanji}\n")
            word_data = query_ojad(browser, kana, timeout=timeout)
            pitch_reading = word_data.find_element(
                By.CLASS_NAME, "phrasing_text"
            ).get_attribute("outerHTML")

        pitch_curve_full = word_data.find_element(
            By.XPATH, f"//*[contains(text(), 'set_accent_curve_phrase')]"
        ).get_attribute("innerHTML")

        # Need to strip all of the garbage javascript syntax
        # surrounding the actual data for the pitch curve
        pcstr_no_curly = re.findall("{(.+?)}", pitch_curve_full)
        assert len(pcstr_no_curly) == 1
        pcstr = re.findall("\((.+?)\)", pcstr_no_curly[0])
        assert len(pcstr) == 1
        pcstr = pcstr[0]

        word_dict[word] = {"pitch reading": pitch_reading, "pitch curve data": pcstr}

        # word_data.screenshot("/tmp/" + word + ".png")
        # word_dict[word] = word_data
        sleep(1 * random.uniform(0, 1))  # Not sure if they'll like ban
        # me or something if I query their website too much
    return word_dict
