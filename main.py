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
import shutil

import pickle as pkl

import genanki

from ingest_data import *
from scrape_tatoeba import *
from genanki_templates import *

import pickle

import argparse


def init_browser(args):
    options = Options()
    options.add_argument("--headless")
    if args.z:
        browser = webdriver.Firefox(
            options=options,
        )
    else:
        # default version
        firefox_dev_binary = FirefoxBinary("/usr/bin/firefox-developer-edition")
        fp = webdriver.FirefoxProfile()
        browser = webdriver.Firefox(
            firefox_binary=firefox_dev_binary,
            executable_path="./geckodriver",
            firefox_profile=fp,
            options=options,
        )
    return browser


# def get_ojad_page(browser):
#     base_url = "https://www.gavo.t.u-tokyo.ac.jp/ojad/phrasing/index"
#     page = browser.get(base_url)
#     return browser

def open_ojad(args):
    browser = init_browser(args)
    base_url = "https://www.gavo.t.u-tokyo.ac.jp/ojad/phrasing/index"
    page = browser.get(base_url)
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
    """
    by default, assume dict2 is newer
    """
    new_dict = {}
    # assert set(dict1.keys()) == set(dict2.keys())
    for key in set(dict1.keys()) | set(dict2.keys()):
        if key not in dict1:
            new_dict[key] = dict2[key]
        elif key not in dict2:
            new_dict[key] = dict1[key]
        else:
            new_dict[key] = dict1[key] | dict2[key]

    return new_dict


def get_no_pitch_words(word_data, words):
    no_pitch_words = set()
    for word in words:
        if word not in word_data or (
            word_data[word]["pitch reading"] + word_data[word]["pitch curve data"] == ""
        ):
            no_pitch_words.add(word)
    return no_pitch_words


def get_no_rei_words(word_data, words):
    no_rei_words = set()
    for word in words:
        if word not in word_data or (
            word_data[word]["audio path"] + word_data[word]["transcript"] == ""
        ):
            no_rei_words.add(word)
    return no_rei_words


def main(args):
    df = get_df()
    lesson_names, tango_by_lesson = get_tango_by_lesson(df)
    anki_ids = get_anki_ids(lesson_names)

    # Start with just lesson 1
    lessons = lesson_names[0:1]
    for lesson in lessons:
        browser = open_ojad(args)
        print("\n\n\n")
        print(lesson)
        print(70 * "=")
        # lesson number and the section (e.g. 会話１) within that lesson
        try:
            lnum, lsec = lesson.split("-")
        except ValueError:
            print(lesson)
        lesson_deck_id = anki_ids[lesson]
        lesson_deck = genanki.Deck(lesson_deck_id, f"Automated-OJAD::{lnum}::{lsec}")

        words = tango_by_lesson[lnum][lsec]

        lesson_pkl = f"./data/{lesson}.pkl"

        try:
            with open(lesson_pkl, "rb") as f:
                word_data = pkl.load(f)
                for word in word_data:
                    # word_data[word]["audio path"] = re.sub(
                    #     "/home/fkobayashi/.local/share/Anki2/User 1/collection.media/",
                    #     "",
                    #     word_data[word]["audio path"],
                    # )
                    # word_data[word]["audio path"] = re.sub(
                    #     "audio/",
                    #     "",
                    #     word_data[word]["audio path"],
                    # )
                    word_data[word]["audio path"] = re.sub(
                        "/", "-", word_data[word]["audio path"]
                    )
        except:  # FileNotFoundError
            subprocess.call(["touch", lesson_pkl])  # so no
            # filenotfound when moving the backup later
            word_data = {}
            # print("word data keys: ", word_data.keys())

        # needs_pitch = get_no_pitch_words(word_data, words)
        # needs_rei = get_no_rei_words(word_data, words)

        # if needs_pitch:
        #     print("\n")
        #     print(70 * "-")
        #     print(f"{len(needs_pitch)} needs pitch data:")
        #     for word in needs_pitch:
        #         print(word)
        #     print("fetching pitch data...")
        #     pitch_data = get_words_pitch(browser, needs_pitch)
        #     # merge my stupid dictionaries
        #     word_data = merge_dicts(word_data, pitch_data)
        # if needs_rei:
        #     print("\n")
        #     print(70 * "-")
        #     print(f"{len(needs_rei)} words need example sentences:")
        #     for word in needs_rei:
        #         print(word)
        #     print("fetching example data...")
        #     rei_data = get_words_rei(browser, needs_rei)
        #     word_data = merge_dicts(word_data, rei_data)

        # Backup data before overwrite
        shutil.move(lesson_pkl, lesson_pkl + ".bak")
        with open(lesson_pkl, "wb") as f:
            pickle.dump(word_data, f)

        for word in words:
            kana, kanji, english, lesson_tag = word
            if kanji:
                reading = kanji
            elif kana:
                reading = kana
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
                    english,
                    transcript,  # example sentence w/ furigana from tatoeba
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
        genanki.Package(lesson_deck).write_to_file(f"./apkgs/{lesson}.apkg")

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-z', action="store_true",help="run in experimental mode")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse()
    main(args)

# def test():
#     browser = open_ojad()
#     words = ["ために", "入学試験", "一生けんめい", "将来"]
#     word_dict = process_words(browser, words)


# def gen_cards():
#     shit_deck = genanki
