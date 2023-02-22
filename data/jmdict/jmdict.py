from pathlib import Path
import zipfile
import json

from sudachipy import tokenizer
from sudachipy import dictionary

from jmdict_tags import *

tokenizer_obj = dictionary.Dictionary(dict="small").create()
mode = tokenizer.Tokenizer.SplitMode.A


SCRIPT_DIR = Path(__file__).parent


def load_dictionary(dictionary):
    output_map = {}
    archive = zipfile.ZipFile(dictionary, "r")

    result = list()
    for file in archive.namelist():
        if file.startswith("term"):
            with archive.open(file) as f:
                data = f.read()
                d = json.loads(data.decode("utf-8"))
                result.extend(d)

    for entry in result:
        if entry[0] in output_map:
            output_map[entry[0]].append(entry)
        else:
            output_map[entry[0]] = [
                entry
            ]  # Using headword as key for finding the dictionary entry
    return output_map


def setup():
    return load_dictionary(str(Path(SCRIPT_DIR, "jmdict_english.zip")))


dictionary_map = setup()


def recursive_tuple(craplist):
    if type(craplist) == list:
        return tuple([recursive_tuple(item) for item in craplist])
    else:
        return craplist


def sort_by_pos(dmap):
    pos_dict = {}
    for key in dmap:
        word = dmap[key]
        for entry in word:
            tags = entry[2].split(" ")
            for tag in tags:
                if tag not in pos_dict:
                    pos_dict[tag] = set()
                else:
                    pos_dict[tag] |= set((recursive_tuple(entry),))
    return pos_dict


pos_dict = sort_by_pos(dictionary_map)

# The part below shows that there are a few verbs that are often
# written in kana alone and which have (apparently) multiple
# conjugation classes. These were
#
# する -- no surprise here I guess... one is to pickpocket (掏る) and
# the other is suru. I am gonna just assume we never have to deal with
# this.
#
# Another is 滑る (なめる). Apparently this is a slightly nonstandard
# reading? So I'm gonna ignore it too.
#
# Another problem is 抉る (こじる). I am gonna ignore this too.
katakana = set(
    " アイウエオ カキクケコ ガギグゲゴ サシスセソ ザジズゼゾ タチツテト ダヂヅデド ナニヌネノ ハヒフヘホ バビブベボ パピプペポ マミムメモ ヤユヨ ラリルレロ ワヰヱヲ"
)

uks = pos_dict["uk"]
uk_crapdict = {}
for uk in uks:
    reading = uk[1]

    # If there's no given reading that seems to always mean that the
    # word given is written in katakana, whence the `kanji` reading is
    # actually katakana.
    if not reading:
        assert set(reading) <= katakana
        reading = uk[0]

    tags = set(uk[2].split(" "))
    num_classes = (
        bool(tags & ichidan)
        + bool(tags & godan)
        + bool(tags & godan_irregular)
        + bool(tags & irregular)
    )
    try:
        assert num_classes <= 1
    except AssertionError:
        print("\ntoo many classes")
        print(num_classes, tags)
        print(uk)

    if reading not in uk_crapdict:
        uk_crapdict[reading] = set()
    else:
        uk_crapdict[reading] |= tags

# Collisions we get here:
# 居る <--> 要る
# 為る <--> 掏る
for reading in uk_crapdict:
    tags = uk_crapdict[reading]
    num_classes = (
        bool(tags & ichidan)
        + bool(tags & godan)
        + bool(tags & godan_irregular)
        + bool(tags & irregular)
    )
    try:
        assert num_classes <= 1
    except AssertionError:
        print("\nAlso too many classes")
        print("-------------")
        print(reading)
        print(uk_crapdict[reading])
        print("-------------")

# Delete problem words
del uk_crapdict["なめる"]
del uk_crapdict["する"]
del uk_crapdict["いる"]
del uk_crapdict["こじる"]


def write_verbs(pos_dict):
    # Map a verb --- i.e. a key of the form
    #    1. kanji + okurigana (if unambiguous),
    #    2. kana (if word usually written in kana alone)
    verb_to_class = {}

    # manual overrides of some dumb collisions
    verb_to_class["する"] = "vs-i"
    verb_to_class["いる"] = "v1"

    # Ignore verbs usually written in kana that can cause problems
    # because of differing conjugation patterns
    # uks_to_ignore = set(["なめる", "いる", "する", "こじる"])

    for vs in pos_dict["vs"]:
        reading = vs[0] + "する"
        if reading in verb_to_class.keys():
            assert verb_to_class[reading] == "vs"
        else:
            verb_to_class[reading] = "vs"

    for tag in acceptable_verbs:
        if tag == "vs":
            continue
        for v in pos_dict[tag]:
            reading = v[0]
            if reading in verb_to_class.keys():
                try:
                    assert verb_to_class[reading] == tag
                except AssertionError:
                    print("\n---------")
                    print(verb_to_class[reading])
                    print(v)
                    print("--------")
            else:
                verb_to_class[reading] = tag

            verb_to_class[reading] = tag

    for reading in uk_crapdict:
        vts = uk_crapdict[reading] & acceptable_verbs
        if vts:
            assert len(vts) == 1
            assert reading not in verb_to_class.keys()
            for vt in vts:
                verb_to_class[reading] = vt

    return verb_to_class


def look_up(word):
    word = word.strip()
    if word not in dictionary_map:
        m = tokenizer_obj.tokenize(word, mode)[0]
        word = m.dictionary_form()
        if word not in dictionary_map:
            return None
    result = [
        {
            "headword": entry[0],
            "reading": entry[1],
            "tags": entry[2],
            "glossary_list": entry[5],
            "sequence": entry[6],
        }
        for entry in dictionary_map[word]
    ]
    return result


def get_verb_class(word):
    if word == "する":
        return "vs"
    if word in ["来る", "くる"]:
        return "vk"
    else:
        entries = look_up(word)
        for entry in entries:
            tags = entry["tags"].split(" ")
