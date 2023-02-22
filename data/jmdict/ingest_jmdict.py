from pathlib import Path
import zipfile
import json

from sudachipy import tokenizer
from sudachipy import dictionary

from jmdict_tags import *

tokenizer_obj = dictionary.Dictionary(dict="small").create()
mode = tokenizer.Tokenizer.SplitMode.A


def read_jmdict():
    SCRIPT_DIR = Path(__file__).parent
    jmdict_path = str(Path(SCRIPT_DIR, "jmdict_english.zip"))

    output_map = {}
    archive = zipfile.ZipFile(jmdict_path, "r")

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


def fuzzy_lookup(word, jmdict):
    word = word.strip()
    if word not in jmdict:
        m = tokenizer_obj.tokenize(word, mode)[0]
        word = m.dictionary_form()
        if word not in jmdict:
            return None
    result = [
        {
            "headword": entry[0],
            "reading": entry[1],
            "tags": entry[2],
            "glossary_list": entry[5],
            "sequence": entry[6],
        }
        for entry in jmdict[word]
    ]
    return result


def recursive_tuple(craplist):
    if type(craplist) == list:
        return tuple([recursive_tuple(item) for item in craplist])
    else:
        return craplist


def sort_by_pos(jmdict):
    pos_dict = {}
    for key in jmdict:
        word = jmdict[key]
        for entry in word:
            tags = entry[2].split(" ")
            for tag in tags:
                if tag not in pos_dict:
                    pos_dict[tag] = set()
                else:
                    pos_dict[tag] |= set((recursive_tuple(entry),))
    return pos_dict


def get_pos_dict():
    jmdict = read_jmdict()
    return sort_by_pos(jmdict)


def get_uk(pos_dict):
    """
    Get a dictionary mapping verbs usually written in kana alone to
    the appropriate conjugation class.

    Find cases where there're multiple `usually written in kana alone`
    verbs with the same kana representation but different conjugation
    patterns.
    """

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
        "アイウエオ カキクケコ ガギグゲゴ サシスセソ ザジズゼゾ タチツテト ダヂヅデド ナニヌネノ ハヒフヘホ バビブベボ パピプペポ マミムメモ ヤユヨ ラリルレロ ワヰヱヲ"
    )

    # Get the usually-kana words
    uks = pos_dict["uk"]

    # We'll keep track of the (v)erb (c)lass here.
    kana_to_vc = {}

    # And any problems here
    problem_keys = set()
    for uk in uks:
        reading = uk[1]

        # If there's no given reading that seems to always mean that the
        # word given is written in katakana, whence the `kanji` reading is
        # actually katakana.
        if not reading:
            assert set(reading) <= katakana
            reading = uk[0]

        # Get parts of speech and other tags
        word_tags = set(uk[2].split(" "))

        # Number of verb classes the word is described as belonging to
        num_classes = len(word_tags & all_valid_verb_tags)

        # (
        #     bool(word_tags & ichidan)
        #     + bool(word_tags & godan)
        #     + bool(word_tags & godan_irregular)
        #     + bool(word_tags & irregular)
        # )
        try:
            assert num_classes <= 1
        except AssertionError:
            print("\nToo many verb tags in entry:")
            print(
                f"{(reading, uk[0])} appeared to belong to {num_classes} verb classes:"
            )
            print(f"tags: {word_tags}")
            problem_keys.add(reading)

        if reading not in kana_to_vc:
            kana_to_vc[reading] = set()
        else:
            kana_to_vc[reading] |= word_tags

            if reading in problem_keys:
                continue

            verb_tags = kana_to_vc[reading] & all_valid_verb_tags

            # Collisions we get here:
            # 居る <--> 要る
            # 為る <--> 掏る

            try:
                assert len(verb_tags) <= 1
            except AssertionError:
                print("\nOverlapping readings:")
                print(
                    f"{(reading, uk[0])} appears to be an ambiguous kana reading (i.e. multiple conjugation classes):"
                )
                print(f"tags: {verb_tags}")
                print(
                    "Printing of further collisions for this kana string will be omitted."
                )
                problem_keys.add(reading)

    print("\n\n------------")
    print("Problem keys:")
    print(problem_keys)

    while problem_keys:
        problem_key = problem_keys.pop()
        del kana_to_vc[problem_key]

    return kana_to_vc


# def write_verbs(pos_dict):

#     for vs in pos_dict["vs"]:
#         reading = vs[0] + "する"
#         if reading in verb_to_class.keys():
#             assert verb_to_class[reading] == "vs"
#         else:
#             verb_to_class[reading] = "vs"

#     for tag in all_valid_verb_tags:
#         if tag == "vs":
#             continue
#         for v in pos_dict[tag]:
#             reading = v[0]
#             if reading in verb_to_class.keys():
#                 try:
#                     assert verb_to_class[reading] == tag
#                 except AssertionError:
#                     print("\n---------")
#                     print(verb_to_class[reading])
#                     print(v)
#                     print("--------")
#             else:
#                 verb_to_class[reading] = tag

#             verb_to_class[reading] = tag

#     for reading in kana_to_vc:
#         vts = kana_to_vc[reading] & all_valid_verb_tags
#         if vts:
#             assert len(vts) == 1
#             assert reading not in verb_to_class.keys()
#             for vt in vts:
#                 verb_to_class[reading] = vt

#     return verb_to_class
