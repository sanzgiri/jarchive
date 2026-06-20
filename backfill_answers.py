#!/usr/bin/env python3
"""
Backfill missing answers in jarchive.csv by re-downloading and re-parsing episodes.

Usage:
    python3 backfill_answers.py [--dry-run] [--batch-size N] [--start-gid N]

This script:
1. Identifies episodes in jarchive.csv that have clues with empty answers
2. Re-downloads those episodes from j-archive.com
3. Re-parses them with the updated parser (supports new HTML format)
4. Updates jarchive.csv with the extracted answers
"""

import os
import sys
import time
import re
import argparse
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from bs4 import BeautifulSoup

SECONDS_BETWEEN_REQUESTS = 2
BASE_URL = "https://j-archive.com/showgame.php?game_id={}"


def find_episodes_missing_answers(csv_path):
    """Find all game IDs that have at least one clue with an empty answer."""
    missing = set()
    with open(csv_path, 'r', encoding='utf-8') as f:
        f.readline()  # skip header
        for line in f:
            parts = line.rstrip('\n').split(' || ')
            if len(parts) == 7:
                gid = int(parts[0])
                answer = parts[6].strip()
                if not answer:
                    missing.add(gid)
    return sorted(missing)


def download_game(game_id):
    """Download a single game page, return HTML or None."""
    url = BASE_URL.format(game_id)
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; jarchive-backfill/1.0)'})
    try:
        response = urlopen(req, timeout=30)
        if response.code == 200:
            return response.read().decode('utf-8', errors='replace')
    except (HTTPError, Exception) as e:
        print(f"  Error downloading game {game_id}: {e}", file=sys.stderr)
    return None


def extract_answer_from_clue(clue_td):
    """Extract the answer from a clue td element using both old and new formats."""
    answer = ""

    # Format 1: <div onmouseover="..."> with inline <em class="correct_response">
    div = clue_td.find("div", onmouseover=True)
    if div:
        mouseover = div.get("onmouseover", "")
        answer_soup = BeautifulSoup(mouseover, "lxml")
        answer_em = answer_soup.find("em", class_="correct_response")
        if not answer_em:
            answer_em = answer_soup.find("em")
        if answer_em:
            answer = answer_em.get_text()

    # Format 2: <em class="correct_response"> in hidden sibling td
    if not answer:
        answer_em = clue_td.find("em", class_="correct_response")
        if answer_em:
            answer = answer_em.get_text(strip=True)

    return answer


def parse_game_answers(html, gid):
    """Parse a game HTML and return a dict mapping (rnd, category, value, text) -> answer."""
    answers = {}
    bsoup = BeautifulSoup(html, "lxml")

    # Parse rounds 1 and 2
    for rnd, round_id in [(1, "jeopardy_round"), (2, "double_jeopardy_round")]:
        r = bsoup.find(id=round_id)
        if not r:
            continue

        categories = [c.get_text() for c in r.find_all("td", class_="category_name")]
        x = 0
        for a in r.find_all("td", class_="clue"):
            if a.get_text().strip():
                answer = extract_answer_from_clue(a)
                if answer:
                    text_elem = a.find("td", class_="clue_text")
                    text = text_elem.get_text() if text_elem else ""
                    cat = categories[x] if x < len(categories) else ""
                    answers[(rnd, cat, text[:50])] = answer
            x = 0 if x == 5 else x + 1

    # Parse Final Jeopardy
    r = bsoup.find("table", class_="final_round")
    if r:
        answer = ""
        div = r.find("div", onmouseover=True)
        if div:
            answer_soup = BeautifulSoup(div.get("onmouseover"), "lxml")
            answer_em = answer_soup.find("em")
            if answer_em:
                answer = answer_em.get_text()
        if not answer:
            answer_em = r.find("em", class_="correct_response")
            if answer_em:
                answer = answer_em.get_text(strip=True)
        if not answer:
            answer_em = r.find("em")
            if answer_em:
                answer = answer_em.get_text(strip=True)
        if answer:
            text_elem = r.find("td", class_="clue_text")
            text = text_elem.get_text() if text_elem else ""
            answers[(3, "", text[:50])] = answer

    return answers


def backfill_csv(csv_path, game_answers_map):
    """Update the CSV file with backfilled answers."""
    lines = []
    updated_count = 0

    with open(csv_path, 'r', encoding='utf-8') as f:
        header = f.readline()
        lines.append(header)
        for line in f:
            parts = line.rstrip('\n').split(' || ')
            if len(parts) == 7 and not parts[6].strip():
                gid = int(parts[0])
                if gid in game_answers_map:
                    rnd = int(parts[2])
                    text = parts[5][:50]
                    cat = parts[3]
                    answers = game_answers_map[gid]
                    # Try to match by (rnd, cat, text_prefix)
                    key = (rnd, cat, text)
                    if key in answers:
                        parts[6] = answers[key]
                        updated_count += 1
                        line = ' || '.join(parts) + '\n'
                    elif (rnd, "", text) in answers:
                        parts[6] = answers[(rnd, "", text)]
                        updated_count += 1
                        line = ' || '.join(parts) + '\n'
            lines.append(line)

    with open(csv_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    return updated_count


def main():
    parser = argparse.ArgumentParser(description="Backfill missing answers in jarchive.csv")
    parser.add_argument("--dry-run", action="store_true", help="Only report what would be done")
    parser.add_argument("--batch-size", type=int, default=50, help="Number of episodes per batch")
    parser.add_argument("--start-gid", type=int, default=0, help="Start from this game ID")
    parser.add_argument("--csv", default="jarchive.csv", help="Path to jarchive.csv")
    args = parser.parse_args()

    csv_path = args.csv
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found", file=sys.stderr)
        sys.exit(1)

    print("Finding episodes with missing answers...")
    missing_gids = find_episodes_missing_answers(csv_path)
    if args.start_gid:
        missing_gids = [g for g in missing_gids if g >= args.start_gid]

    print(f"Found {len(missing_gids)} episodes with missing answers")

    if args.dry_run:
        print(f"Would download and re-parse {len(missing_gids)} episodes")
        print(f"First 20: {missing_gids[:20]}")
        return

    # Process in batches
    total_updated = 0
    for i in range(0, len(missing_gids), args.batch_size):
        batch = missing_gids[i:i + args.batch_size]
        print(f"\nBatch {i // args.batch_size + 1}: games {batch[0]}-{batch[-1]} ({len(batch)} episodes)")

        game_answers_map = {}
        for gid in batch:
            html = download_game(gid)
            if html:
                answers = parse_game_answers(html, gid)
                if answers:
                    game_answers_map[gid] = answers
                    print(f"  Game {gid}: found {len(answers)} answers")
                else:
                    print(f"  Game {gid}: no answers found in HTML")
            time.sleep(SECONDS_BETWEEN_REQUESTS)

        if game_answers_map:
            updated = backfill_csv(csv_path, game_answers_map)
            total_updated += updated
            print(f"  Updated {updated} clues in CSV")

    print(f"\nDone! Total clues updated: {total_updated}")


if __name__ == "__main__":
    main()
