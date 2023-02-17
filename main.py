import shutil

import genanki

from ingest_data import *
from scrape_ojad import *
from scrape_tatoeba import *
from genanki_templates import *

import os

from pathlib import Path
import argparse

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

def generate_jisho_links(kanji_list):
    """
    given a list of kanji for a single card/item, generate a single string containing links to all kanji
    """
    s = ""
    for kanji in kanji_list:
        s += f"https://jisho.org/search{kanji}%23kanji\n"
    s = s[:-1]
    return s

def check_paths_exist():
    if not os.path.exists("./data/jsons/"):
        os.mkdir("./data/jsons")
    if not os.path.exists("./data/backups/"):
        os.mkdir("./data/backups")
    if not os.path.exists("./apkgs"):
        os.mkdir("./apkgs")

def make_core_deck(lesson, anki_ids, tango_by_lesson, args):
    browser = open_ojad(args)
    try:
        lnum, lsec = lesson.split("-")
    except ValueError as e:
        print(lesson)
        raise e

    lesson_deck_id = anki_ids[lesson]
    lesson_deck = genanki.Deck(lesson_deck_id, f"Automated-OJAD::{lnum}::{lsec}")

    words = tango_by_lesson[lnum][lsec]

    if args.debug:
        print(f"words {words}")

    lesson_json = f"./data/jsons/{lesson}.json"

    print(lesson_json)
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

    print(needs_pitch)
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
        
        kanji_list = get_kanji(kanji)
        jisho_links = generate_jisho_links(kanji_list)

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
                "" + jisho_links,  # special notes
                lesson,
                f"[sound:{audio_path}]",  # example sentence audio
                "",  # front sound
            ],
        )
        lesson_deck.add_note(word_note)
    genanki.Package(lesson_deck).write_to_file(f"./apkgs/{lesson}.apkg")

def make_kanji_deck(lesson, anki_ids_kanji, tango_by_lesson, args):
    try:
        lnum, lsec = lesson.split("-")
    except ValueError as e:
        print(lesson)
        raise e
    lesson_deck_id = anki_ids_kanji[lesson]
    lesson_deck = genanki.Deck(lesson_deck_id, f"Automated-kanji::{lnum}::{lsec}")
    words = tango_by_lesson[lnum][lsec]

    for word in words:
        kana, kanji, english, lesson_tag = word
        if kanji:
            for k in get_kanji(kanji):
                kanji_note = genanki.Note(
                    model=automated_kanji_model,
                    fields=[
                        k,
                        "", # kun readings
                        "", # on readings
                        "", # example words
                        "", # example sentences
                    ]
                )
        lesson_deck.add_note(kanji_note)
    genanki.Package(lesson_deck.write_to_file(f"./apkgs/{lesson}_kanji.apkg"))

def main(args):
    check_paths_exist()
    df = get_df()
    lesson_names, tango_by_lesson = get_tango_by_lesson(df)
    anki_ids = get_anki_ids(lesson_names)
    anki_ids_kanji = get_anki_ids(lesson_names, 'kanji')

    if args.debug:
        print(f"df {df}")
        print(f"lesson_names {lesson_names}")
        print(f"anki_ids {anki_ids}")

    # Determine which lessons to produce decks for
    if args.lesson_index:
        lessons = [lesson_names[i] for i in args.lesson_index]
    else:
        # TODO
        lessons = lesson_names[0:1]

    for lesson in lessons:
        print("\n\n\n")
        print(lesson)
        print(70 * "=")
        # lesson number and the section (e.g. 会話１) within that lesson
        if args.core:
            make_core_deck(lesson, anki_ids, tango_by_lesson, args)
        elif args.kanji:
            make_kanji_deck(lesson, anki_ids_kanji, tango_by_lesson, args)

def clean():
    confirmation = input("delete .apkg, .pkl, and .json files? (y/n)")
    if confirmation.lower() == "y":
        print("cleaning out directories")
        apkgs_folder = Path("./apkgs")
        data_folder = Path("./data")
        backup_folder = Path("./data/backups")
        json_folder = Path("./data/jsons")
        for file in apkgs_folder.glob("*.apkg"):
            file.unlink()
        for file in data_folder.glob("*.pkl"):
            file.unlink()
        for file in data_folder.glob("*.bak"):
            file.unlink()
        for file in backup_folder.glob("*.bak"):
            file.unlink()
        for file in json_folder.glob("*.json"):
            file.unlink()
    else:
        print("cancelling")

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-z', action="store_true",help="run in experimental mode")
    parser.add_argument('--lesson_index', nargs="*", type=int, help="indices of the lessons to collect")
    parser.add_argument('--clean', action="store_true", help="removes .apkg, .pkl, and .pkl.bak files")
    parser.add_argument('--generate', action="store_true", help="run main and generate files")
    parser.add_argument('--core', action="store_true", help="generate core decks")
    parser.add_argument('--kanji', action="store_true", help="generate additional kanji decks")
    parser.add_argument('--debug', action="store_true", help="turns on printing for just about everything")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse()
    if args.debug:
        print(args)
    if args.clean:
        clean()
    if args.generate:
        main(args)
