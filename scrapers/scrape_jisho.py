from selenium.webdriver.common.by import By
from IPython import embed
from tqdm import tqdm as tqdm

import ingest_data # What have I just wrought upon this unholy land
import scrapers.browser_setup as browser_setup

def query_jisho(browser, kanji):
    prefix = r"https://jisho.org/search/"
    suffix = r"%23kanji"
    browser.get(f"{prefix}{kanji}{suffix}")
    browser_setup.wait_for_element(browser, By.CLASS_NAME, "kanji-details__main-readings", kanji)
    browser_setup.wait_for_element(browser, By.CLASS_NAME, "kanji-details__main-meanings", kanji)
    return browser

def get_kanji_data(browser):
    meanings = browser.find_element(By.CLASS_NAME, "kanji-details__main-meanings")
    meanings = meanings.get_attribute("innerHTML")
    # meanings = meanings.split(":")[1]

    # important to note that not all  kanji will have both kun and on yomi
    readings = browser.find_element(By.CLASS_NAME, "kanji-details__main-readings")
    readings = readings.text.split("\n") # splits between the on and kun yomi
    print(readings)
    yomi = {}
    yomi["kun"] = ""
    yomi["on"] = ""
    for read in readings:
        if read[:3].lower() == "kun":
            yomi["kun"] = read[5:]
        elif read[:2].lower() == "on":
            yomi["on"] = read[4:]
    # kun_entry = readings.find_element(By.CLASS_NAME, "kun_yomi")
    # kun_list = kun_entry.find_element(By.CLASS_NAME, 'kanji-details__main-readings-list')
    # kun_yomi = kun_list.text.strip()
    # on_entry = readings.find_element(By.CLASS_NAME, "on_yomi")
    # on_list = on_entry.find_element(By.CLASS_NAME, 'kanji-details__main-readings-list')
    # on_yomi = on_list.text.strip()
    return meanings.strip(), yomi["kun"], yomi["on"] 

def split_kanji_data(kanji_data):
    """
    kanji data is the tuple from get_kanji_data
    """
    meanings = kanji_data[0].split(".")
    meanings = [i.strip() for i in meanings] 
    kun_yomi = kanji_data[1].split("、")
    kun_yomi = [i.strip() for i in kun_yomi]
    on_yomi = kanji_data[2].split("、")
    on_yomi = [i.strip() for i in on_yomi]
    return meanings, kun_yomi, on_yomi

def get_words_meaning(browser, words, timeout=10):
    """
    This one expects "words" to be a collection of tuples of the form
    (kana, kanji, english, lesson)
    """
    word_dict = {}
    for word in tqdm(words):
        kana, kanji, english, lesson = word
        if kanji:
            kanji_list = ingest_data.get_kanji(kanji)
            meaning_string = ""
            for k in kanji_list:
                query_jisho(browser, k)
                data = get_kanji_data(browser)
                meanings, _, _ = split_kanji_data(data)
                meaning_string += k + ":" + (", ".join(meanings)) + "\n"
            word_dict[word] = {"meaning": meaning_string}
        else:
            word_dict[word] = {"meaning": ""}
    return word_dict

if __name__ == "__main__":
    # python -m scrapers.scrape_jisho
    browser = browser_setup.init_browser(mode="headed")
    test_kanji = "会"
    browser = query_jisho(browser, test_kanji)
    embed()
    meanings = get_kanji_data(browser)
    browser.close()
    print(meanings)
