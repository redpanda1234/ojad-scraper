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


import subprocess
import pathlib
import pandas as pd

from ingest_data import clean_word


def query_tatoeba(browser, word):
    prefix = r"https://tatoeba.org/en/sentences/search?from=jpn&has_audio=yes&native=&orphans=no&query="
    suffix = r"&sort=relevance&sort_reverse=&tags=&to=eng&trans_filter=limit&trans_has_audio=&trans_link=&trans_orphan=&trans_to=&trans_unapproved=&trans_user=&unapproved=no&user="
    browser.get(f"{prefix}{word}{suffix}")
    return browser


def wait_for_element(browser, By_what, trigger_string, kanji_string, timeout=5):
    try:
        element_loaded = EC.presence_of_element_located((By_what, trigger_string))
        WebDriverWait(browser, timeout).until(element_loaded)

    except TimeoutException:
        print(f"Timed out on word {kanji_string}")


# いい例
def get_ii_rei(browser, kanji_string, lesson, timeout=5):
    result_page = query_tatoeba(browser, clean_word(kanji_string))
    # wait for text box to appear and then enter our kanji string into it
    wait_for_element(browser, By.CLASS_NAME, "sentence", kanji_string, timeout=timeout)
    sent = browser.find_element(By.CLASS_NAME, "sentence")

    wait_for_element(
        sent,
        By.XPATH,
        "//*[contains(@href, 'tatoeba.org/en/audio/download')]",
        kanji_string,
        timeout=timeout,
    )
    audio_url = sent.find_element(
        By.XPATH, "//*[contains(@href, 'tatoeba.org/en/audio/download')]"
    ).get_attribute("href")

    lesson_path = (
        f"/home/fkobayashi/.local/share/Anki2/User 1/collection.media/audio/{lesson}"
    )
    pathlib.Path(lesson_path).mkdir(parents=True, exist_ok=True)
    local_audio_path = f"{lesson_path}/{kanji_string}.mp3"

    subprocess.run(["curl", "-s", "-L", audio_url, "--output", local_audio_path])

    # request pitch analysis
    wait_for_element(
        browser, By.CLASS_NAME, "transcription", kanji_string, timeout=timeout
    )
    transcript = (
        browser.find_element(By.CLASS_NAME, "transcription")
        .find_element(By.CLASS_NAME, "text")
        .get_attribute("innerHTML")
    )

    return local_audio_path, transcript


# def process_words(browser, words, timeout=5):
#     word_dict = {}
#     for word in tqdm(words):
#         word_data = query_ojad(browser, word, timeout=timeout)
#         # word_data.screenshot("/tmp/" + word + ".png")
#         word_dict[word] = word_data.get_attribute("outerHTML")
#         sleep(2 * random.uniform(0, 1))  # Not sure if they'll like ban
#         # me or something if I query their website too much
#     return word_dict


def nt_words_rei(browser, words, timeout=15):
    """
    This one expects "words" to be a collection of named tuples
    """
    word_dict = {}
    for word in tqdm(words):
        try:
            if not pd.isna(word.kanji):
                word_data = get_ii_rei(
                    browser, word.kanji, word.lesson, timeout=timeout
                )
            elif not pd.isna(word.kana):
                word_data = get_ii_rei(browser, word.kana, word.lesson, timeout=timeout)
            else:
                assert False
            local_audio_path, transcript = word_data

        except:  # timeout
            local_audio_path = ""
            transcript = ""

        word_dict[word] = {"audio path": local_audio_path, "transcript": transcript}

        # word_data.screenshot("/tmp/" + word + ".png")
        # word_dict[word] = word_data
        # sleep(5 * random.uniform(0, 1))  # Not sure if they'll like ban
        # me or something if I query their website too much
    return word_dict
