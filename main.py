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

import genanki

from ingest_data import *
from scrape_tatoeba import *
from genanki_templates import *


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


# def process_words(browser, words, timeout=5):
#     word_dict = {}
#     for word in tqdm(words):
#         word_data = query_ojad(browser, word, timeout=timeout)
#         # word_data.screenshot("/tmp/" + word + ".png")
#         word_dict[word] = word_data.get_attribute("outerHTML")
#         sleep(2 * random.uniform(0, 1))  # Not sure if they'll like ban
#         # me or something if I query their website too much
#     return word_dict


def nt_words_pitch(browser, words, timeout=5):
    """
    This one expects "words" to be a collection of named tuples
    """
    word_dict = {}
    for word in tqdm(words):
        if not pd.isna(word.kanji):
            word_data = query_ojad(browser, word.kanji, timeout=timeout)
        elif not pd.isna(word.kana):
            word_data = query_ojad(browser, word.kana, timeout=timeout)
        else:
            assert False

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


def merge_dicts(dict1, dict2):
    new_dict = {}
    assert set(dict1.keys()) == set(dict2.keys())
    for key in dict1:
        new_dict[key] = dict1[key] | dict2[key]
    return new_dict


def main():
    browser = open_ojad()

    df = get_df()
    lesson_names, tango_by_lesson = get_tango_by_lesson(df)
    anki_ids = get_anki_ids(lesson_names)

    # Start with just lesson 1
    lessons = lesson_names[0:1]
    for lesson in lessons:
        print(lesson)
        # lesson number and the section (e.g. 会話１) within that lesson
        try:
            lnum, lsec = lesson.split("-")
        except ValueError:
            print(lesson)
        lesson_deck_id = anki_ids[lesson]
        lesson_deck = genanki.Deck(lesson_deck_id, f"Automated-OJAD::{lnum}::{lsec}")

        words = tango_by_lesson[lnum][lsec]

        print("fetching pitch data...")
        pitch_data = nt_words_pitch(browser, words)
        print("fetching example data...")
        rei_data = nt_words_rei(browser, words)

        # merge my stupid dictionaries
        word_data = merge_dicts(pitch_data, rei_data)

        for word in words:
            if not pd.isna(word.kanji):
                reading = word.kanji
            elif not pd.isna(word.kana):
                reading = word.kana
            else:
                assert False

            pitch_reading, pitch_curve_data, audio_path, transcript = (
                word_data[word]["pitch reading"],
                word_data[word]["pitch curve data"],
                word_data[word]["audio path"],
                word_data[word]["transcript"],
            )
            # print(pitch_reading)

            word_note = genanki.Note(
                model=automated_ojad_model,
                fields=[
                    reading,
                    word.english,
                    transcript,  # example sentence
                    "",  # kanji meaning support might come later
                    "",  # part of speech support might come later
                    pitch_curve_data,  # pitch curve data
                    pitch_reading,  # pitch curve reading
                    "",  # special notes
                    lesson,
                    f"[sound:{audio_path}]",  # example sentence audio
                    "",  # front sound
                ],
            )
            lesson_deck.add_note(word_note)
        genanki.Package(lesson_deck).write_to_file(f"./ojadtest-{lesson}.apkg")


# def test():
#     browser = open_ojad()
#     words = ["ために", "入学試験", "一生けんめい", "将来"]
#     word_dict = process_words(browser, words)


# def gen_cards():
#     shit_deck = genanki
