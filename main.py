import shutil

import genanki

from ingest_data import *
from scrape_ojad import *
from scrape_tatoeba import *
from genanki_templates import *

import os


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


def main():
    df = get_df()

    lesson_names, tango_by_lesson = get_tango_by_lesson(df)
    anki_ids = get_anki_ids(lesson_names)

    # Start the first 34 lesson sections
    lessons = lesson_names[0:34]
    for lesson in lessons:
        browser = open_ojad()
        print("\n\n\n")
        print(lesson)
        print(70 * "=")
        # lesson number and the section (e.g. 会話１) within that lesson
        try:
            lnum, lsec = lesson.split("-")
        except ValueError as e:
            print(lesson)
            raise e

        lesson_deck_id = anki_ids[lesson]
        lesson_deck = genanki.Deck(lesson_deck_id, f"Automated-OJAD::{lnum}::{lsec}")

        words = tango_by_lesson[lnum][lsec]

        lesson_json = f"./data/jsons/{lesson}.json"

        # print(lesson_json)
        if not os.path.exists("./data/jsons/"):
            os.mkdir("./data/jsons")

        if not os.path.exists("./data/backups/"):
            os.mkdir("./data/backups")

        if not os.path.exists("./apkgs"):
            os.mkdir("./apkgs")

        no_preexisting_json = True
        try:
            word_data = read_from_json(lesson_json)
        except:  # FileNotFoundError
            no_preexisting_json = False
            subprocess.call(["touch", lesson_json])  # so no
            # filenotfound when moving the backup later
            word_data = {}
            # print("word data keys: ", word_data.keys())

        needs_pitch = get_no_pitch_words(word_data, words)
        needs_rei = get_no_rei_words(word_data, words)

        # print(f"Words needing pitch info:\n{needs_pitch}")
        if needs_pitch:
            print("\n")
            print(70 * "-")
            print(f"{len(needs_pitch)} needs pitch data:")
            for word in needs_pitch:
                print(word)
            print("fetching pitch data...")
            pitch_data = get_words_pitch(browser, needs_pitch)
            # merge my stupid dictionaries
            word_data = merge_dicts(word_data, pitch_data)
        if needs_rei:
            print("\n")
            print(70 * "-")
            print(f"{len(needs_rei)} words need example sentences:")
            for word in needs_rei:
                print(word)
            print("fetching example data...")
            rei_data = get_words_rei(browser, needs_rei)
            word_data = merge_dicts(word_data, rei_data)

        # Backup data before overwrite
        if not no_preexisting_json:
            shutil.move(lesson_json, f"./data/backups/{lesson}.json.bak")
        dump_to_json(word_data, lesson_json)

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


# def test():
#     browser = open_ojad()
#     words = ["ために", "入学試験", "一生けんめい", "将来"]
#     word_dict = process_words(browser, words)


# def gen_cards():
#     shit_deck = genanki
