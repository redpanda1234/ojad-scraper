import pandas as pd
from collections import namedtuple
from functools import cmp_to_key

from pandas.io import excel

import json
import re
import os


def read_from_json(fname):
    with open(fname, "r") as f:
        word_data = json.load(f)
    new_dict = {}
    for key in word_data:
        # Key is a string like
        # ('ちょうし', '調子', 'condition; state', 'L.5-会2')
        # i.e. (kana, kanji, english, lesson).
        # has to be string because json requires it.
        # 2:-2 --> remove the (' [...] ') wrapping the tuple
        fields = key[2:-2].split("', '")
        new_key = tuple(fields)
        try:
            assert str(new_key) == key
        except AssertionError as e:
            print(f"\nFailed to reconstruct key \n{key}\nin jston step.")
            print(f"Got {new_key} instead.")
            raise e
        new_dict[new_key] = word_data[key]
    return new_dict


def dump_to_json(word_data, fname):
    new_dict = {}
    for key in word_data:
        new_dict[str(key)] = word_data[key]
    print(fname)
    with open(fname, "w") as f:
        json.dump(new_dict, f)


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

def get_kanji(text):
    """
    given a string, return a list of all kanji in the string

    Args:
        text: the text to parse all kanji from
    Returns:
        kanji_list: a list of kanji characters
    """
    kanji_regex = r'[㐀-䶵一-鿋豈-頻]'
    return re.findall(kanji_regex, text)

def get_df():
    """
    read in the vocabulary csv, downloaded from https://ij.japantimes.co.jp/resource/sakuin.jsp
    """
    return pd.read_excel("data/tango.ods")

def get_tango_by_lesson(df):
    """
    Sort the vocab from the vocabulary csv into lesson categories

    Args:
        data frame from get_df
    
    Returns:
        A tuple (lesson_names, tango_by_lesson)
        lesson_names: a list of lesson numbers and sections
        tango_by_lesson is a dict of dicts
    """
    # Filter out all of the section headers in the index (section
    # headers are the first kana in the word in the section)
    tango = df[~df["lesson"].isna()]

    lesson_names = set()
    tango_by_lesson = {}
    for word in tango.iterrows():
        # word is a tuple (index, row_entry) where index is I believe
        # the index in the original dataframe. Also, some words appear
        # in multiple lessons, which is denoted by something like
        # "L.13-速; L.14-読". We want to extract all unique lesson
        # names so that we know exactly what to make the keys for our
        # dictionary that will hold all the vocab from each lesson. So
        # we do that here.
        #
        # First we need to make it hashable.
        #
        # Remove just the square brackets that for some reason all
        # kanji readings were wrapped in
        if not pd.isna(word[1]["kanji"]):
            word[1]["kanji"] = word[1]["kanji"].replace("［", "").replace("］", "")

        # wt == "word tuple" --> hashable.
        wt = un_nan_tuple(tuple(word[1]))  # the 0 index contains the index in the csv
        for lesson in wt[-1].split("; "):
            lesson_names.add(lesson)
            # lesson number, and the subsection within that lesson
            # number
            try:
                lnum, lsec = lesson.split("-")
            except ValueError:
                print(f"word {word} has corrupted lesson string.")
            if lnum not in tango_by_lesson:
                tango_by_lesson[lnum] = {}
            if lsec not in tango_by_lesson[lnum]:
                tango_by_lesson[lnum][lsec] = set()

            tango_by_lesson[lnum][lsec].add(wt)

    # Sort all the lessons
    lesson_names = sorted(list(lesson_names), key=cmp_to_key(compare_lesson_strings))

    return lesson_names, tango_by_lesson


def lesson_ordering(char1, char2):
    """
    Implement the ordering
    T < 会 < 読 < 運 < 聞 < 速
    """
    if char1 == char2:
        return 0

    # cd --> chardict
    cd = {"T": 0, "会": 1, "読": 2, "運": 3, "聞": 4, "速": 5}
    return 2 * (cd[char1] > cd[char2]) - 1


def compare_lesson_strings(s1, s2):
    if s1 == s2:
        return 0

    lnum1, lsec1 = s1.split("-")
    lnum2, lsec2 = s2.split("-")

    # trim the leading L
    lnum1_actual = int(lnum1.split(".")[1])
    lnum2_actual = int(lnum2.split(".")[1])
    if lnum1_actual != lnum2_actual:
        return 2 * (lnum1_actual > lnum2_actual) - 1
    else:
        char1, char2 = lsec1[0], lsec2[0]
        tail1, tail2 = lsec1[1:], lsec2[1:]
        if char1 == char2:
            return 2 * (int(tail1) > int(tail2)) - 1

        return lesson_ordering(char1, char2)


def get_anki_ids(lesson_names, deck_type='core'):
    """
    creates unique identifiers for the decks

    Args:
        lesson_names: A list of lesson numbers and sections
    """
    # see https://www.reddit.com/r/Anki/comments/i1azpt/why_does_genanki_require_both_the_model_id_and/
    anki_ids = {}
    if deck_type == 'core':
        default_anki_id = 1598313698029
    elif deck_type == 'kanji':
        default_anki_id = 1598313699029
    else:
        raise Exception("unrecognized deck_type")

    # lesson names list
    for (i, lesson) in enumerate(lesson_names):
        # I hate this so much | me too
        anki_ids[lesson] = default_anki_id + i
    return anki_ids
