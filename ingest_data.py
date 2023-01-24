import pandas as pd
from collections import namedtuple

from pandas.io import excel


def get_df():
    """
    read in the vocabulary csv, downloaded from https://ij.japantimes.co.jp/resource/sakuin.jsp
    """
    return pd.read_csv("data/tango.csv")


def sort_into_chapters(df):
    """
    Sort the vocab from the vocabulary csv into lesson categories
    """
    # Filter out all of the section headers in the index (section
    # headers are the first kana in the word in the section)
    tango = df[~df["lesson"].isna()]

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
        # First we need to make it hashable. wt == word tuple

        tname = (
            word[1]["kana"]
            .replace("～", "")
            .replace("(", "")
            .replace(")", "")
            .replace("…", "")
            .replace("・", "")
        )
        wt = namedtuple(tname, word[1].index)(*word[1])
        for lesson in word[1]["lesson"].split("; "):
            # lesson number, and the subsection within that lesson
            # number
            lnum, lsec = lesson.split("-")
            if lnum not in tango_by_lesson:
                tango_by_lesson[lnum] = {}
            if lsec not in tango_by_lesson[lnum]:
                tango_by_lesson[lnum][lsec] = set()

            tango_by_lesson[lnum][lsec].add(wt)
    return tango_by_lesson


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


def get_anki_ids(df):
    # see https://www.reddit.com/r/Anki/comments/i1azpt/why_does_genanki_require_both_the_model_id_and/
    anki_ids = {}
    default_anki_id = 1598313698029

    # Filter out all of the section headers in the index (section
    # headers are the first kana in the word in the section)
    tango = df[~df["lesson"].isna()]

    lessons = set()
    for word in tango.iterrows():
        for lesson in word[1]["lesson"].split("; "):
            lessons.add(lesson)
