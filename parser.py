#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from glob import glob

import argparse
import os
import re

def main(args):
    """Loop thru all the games and parse them."""

    print("gid, airdate, rnd, category, value, text, answer")
    for i, file_name in enumerate(glob(os.path.join(args.dir, "*.html")), 1):
        with open(os.path.abspath(file_name)) as f:
            parse_game(f, i)


def parse_game(f, gid):
    """Parses an entire Jeopardy! game and extract individual clues."""
    bsoup = BeautifulSoup(f, "lxml")
    # The title is in the format: `J! Archive - Show #XXXX, aired 2004-09-16`,
    # where the last part is all that is required
    airdate = bsoup.title.get_text().split()[-1]
    if not parse_round(bsoup, 1, gid, airdate) or not parse_round(bsoup, 2, gid, airdate):
        # One of the rounds does not exist
        pass
    # The final Jeopardy! round
    r = bsoup.find("table", class_="final_round")
    if not r:
        # This game does not have a final clue
        return
    category = r.find("td", class_="category_name").get_text()
    text = r.find("td", class_="clue_text").get_text()
    answer = BeautifulSoup(r.find("div", onmouseover=True).get("onmouseover"), "lxml")
    answer = answer.find("em").get_text()
    # False indicates no preset value for a clue
    insert([gid, airdate, 3, category, False, text, answer])


def parse_round(bsoup, rnd, gid, airdate):
    """Parses and inserts the list of clues from a whole round."""
    round_id = "jeopardy_round" if rnd == 1 else "double_jeopardy_round"
    r = bsoup.find(id=round_id)
    # The game may not have all the rounds
    if not r:
        return False
    # The list of categories for this round
    categories = [c.get_text() for c in r.find_all("td", class_="category_name")]
    # The x_coord determines which category a clue is in
    # because the categories come before the clues, we will
    # have to match them up with the clues later on.
    x = 0
    for a in r.find_all("td", class_="clue"):
        is_missing = True if not a.get_text().strip() else False
        if not is_missing:
            value = a.find("td", class_=re.compile("clue_value")).get_text().lstrip("D: $")
            text = a.find("td", class_="clue_text").get_text()
            answer = BeautifulSoup(a.find("div", onmouseover=True).get("onmouseover"), "lxml")
            answer = answer.find("em", class_="correct_response").get_text()
            insert([gid, airdate, rnd, categories[x], value, text, answer])
        x = 0 if x == 5 else x + 1
    return True


def insert(clue):
        print(clue[0], '||' , clue[1], '||', clue[2], '||', clue[3], '||', clue[4], '||', clue[5], '||', clue[6])
        return



if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Parse games from the J! Archive website.", add_help=False,
        usage="%(prog)s [options]")

    parser.add_argument("-d", "--dir", dest="dir", metavar="<folder>",
                        help="the directory containing the game files",
                        default="j-archive")
    parser.add_argument("-n", "--number-of-files", dest="num_of_files",
                        metavar="<number>", help="the number of files to parse",
                        type=int)

    main(parser.parse_args())
#    main()
