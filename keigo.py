import shutil

import genanki

from ingest_data import *
from scrape_ojad import *
from scrape_tatoeba import *
from keigo_template import *

import os

import pandas as pd
from functools import cmp_to_key

from pandas.io import excel

import os


def un_nan_tuple(tup):
    """
    Apparently the nan values cause issues where you can have a set or
    something with multiple distinct nan values and this makes it hard
    later to check what words we've looked up already. To that end we
    remove all nans and replace them with empty strings.
    """
    return tuple([el if not pd.isna(el) else "" for el in tup])


def clean_word(word):
    return (
        word.replace("～", "")
        .replace("(", "")
        .replace(")", "")
        .replace("…", "")
        .replace("・", "")
        .replace("［", "")
        .replace("］", "")
    )


def get_df():
    """
    read in the vocabulary csv, downloaded from https://ij.japantimes.co.jp/resource/sakuin.jsp
    """
    return pd.read_excel("data/keigo.ods")


def get_anki_id():
    # see https://www.reddit.com/r/Anki/comments/i1azpt/why_does_genanki_require_both_the_model_id_and/
    return 1598313698028


def main():
    df = get_df()

    anki_id = get_anki_id()

    # browser = open_ojad()

    lesson_deck = genanki.Deck(anki_id, f"Japanese::Automated-OJAD::L.6::keigo")

    for word in df.iterrows():
        word_info = un_nan_tuple(list(word[1]))
        word_note = genanki.Note(model=keigo_card, fields=word_info)
        lesson_deck.add_note(word_note)
    genanki.Package(lesson_deck).write_to_file(f"./apkgs/L.6-keigo.apkg")

    # needs_pitch = get_no_pitch_words(word_data, words)
    # needs_rei = get_no_rei_words(word_data, words)

    # # print(f"Words needing pitch info:\n{needs_pitch}")
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

    # # Backup data before overwrite
    # if not no_preexisting_json:
    #     shutil.move(lesson_json, f"./data/backups/{lesson}.json.bak")
    # dump_to_json(word_data, lesson_json)

    # for word in words:
    #     kana, kanji, english, lesson_tag = word
    #     if kanji:
    #         reading = kanji
    #     elif kana:
    #         reading = kana
    #     else:
    #         assert False

    #     pitch_reading, pitch_curve_data, audio_path, transcript = (
    #         word_data[word]["pitch reading"],
    #         word_data[word]["pitch curve data"],
    #         word_data[word]["audio path"],
    #         word_data[word]["transcript"],
    #     )
    #     # print(pitch_reading)

    #     word_note = genanki.Note(
    #         model=automated_ojad_model,
    #         fields=[
    #             reading,
    #             english,
    #             transcript,  # example sentence w/ furigana from tatoeba
    #             "",  # kanji meaning support might come later
    #             "",  # part of speech support might come later
    #             pitch_curve_data,  # pitch curve data
    #             pitch_reading,  # pitch curve reading
    #             "",  # special notes
    #             lesson,
    #             f"[sound:{audio_path}]",  # example sentence audio
    #             "",  # front sound
    #         ],
    #     )
    #     lesson_deck.add_note(word_note)
    #     genanki.Package(lesson_deck).write_to_file(f"./apkgs/{lesson}.apkg")


# def test():
#     browser = open_ojad()
#     words = ["ために", "入学試験", "一生けんめい", "将来"]
#     word_dict = process_words(browser, words)


# def gen_cards():
#     shit_deck = genanki
