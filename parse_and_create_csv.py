#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Parse downloaded Jeopardy games and create a CSV file compatible with jarchive_2023.csv
"""

from bs4 import BeautifulSoup
from glob import glob
import os
import sys
import re

def parse_game(filepath):
    """Parse a single game file and return all clues."""
    clues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            bsoup = BeautifulSoup(f, "lxml")
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return clues
    
    # Extract game ID from filename
    gid = int(os.path.basename(filepath).replace('.html', ''))
    
    # Extract airdate from title
    try:
        title = bsoup.title.get_text()
        airdate = title.split()[-1]
    except:
        print(f"Warning: Could not extract airdate for game {gid}", file=sys.stderr)
        airdate = "UNKNOWN"
    
    # Parse Jeopardy round (round 1)
    clues.extend(parse_round(bsoup, 1, gid, airdate))
    
    # Parse Double Jeopardy round (round 2)
    clues.extend(parse_round(bsoup, 2, gid, airdate))
    
    # Parse Final Jeopardy (round 3)
    clues.extend(parse_final_jeopardy(bsoup, gid, airdate))
    
    return clues

def parse_round(bsoup, rnd, gid, airdate):
    """Parse a regular Jeopardy round (1 or 2)."""
    clues = []
    round_id = "jeopardy_round" if rnd == 1 else "double_jeopardy_round"
    r = bsoup.find(id=round_id)
    
    if not r:
        return clues
    
    # Get categories
    categories = [c.get_text() for c in r.find_all("td", class_="category_name")]
    
    # Parse clues
    x = 0
    for a in r.find_all("td", class_="clue"):
        is_missing = not a.get_text().strip()
        
        if not is_missing:
            try:
                value_elem = a.find("td", class_=re.compile("clue_value"))
                if value_elem:
                    value = value_elem.get_text().lstrip("D: $").replace(',', '')
                else:
                    value = ""
                
                text_elem = a.find("td", class_="clue_text")
                text = text_elem.get_text() if text_elem else ""
                
                # Extract answer
                answer = ""
                div = a.find("div", onmouseover=True)
                if div:
                    answer_soup = BeautifulSoup(div.get("onmouseover"), "lxml")
                    answer_em = answer_soup.find("em", class_="correct_response")
                    if answer_em:
                        answer = answer_em.get_text()
                
                clues.append([gid, airdate, rnd, categories[x], value, text, answer])
            except Exception as e:
                print(f"Error parsing clue in game {gid}, round {rnd}: {e}", file=sys.stderr)
        
        x = 0 if x == 5 else x + 1
    
    return clues

def parse_final_jeopardy(bsoup, gid, airdate):
    """Parse Final Jeopardy round."""
    clues = []
    r = bsoup.find("table", class_="final_round")
    
    if not r:
        return clues
    
    try:
        category_elem = r.find("td", class_="category_name")
        category = category_elem.get_text() if category_elem else ""
        
        text_elem = r.find("td", class_="clue_text")
        text = text_elem.get_text() if text_elem else ""
        
        # Extract answer
        answer = ""
        div = r.find("div", onmouseover=True)
        if div:
            answer_soup = BeautifulSoup(div.get("onmouseover"), "lxml")
            answer_em = answer_soup.find("em")
            if answer_em:
                answer = answer_em.get_text()
        
        # Final Jeopardy has no preset value (False in original code)
        clues.append([gid, airdate, 3, category, "False", text, answer])
    except Exception as e:
        print(f"Error parsing Final Jeopardy in game {gid}: {e}", file=sys.stderr)
    
    return clues

def format_clue(clue):
    """Format a clue as a CSV row with || separator."""
    return " || ".join(str(field) for field in clue)

def main(input_dir, output_file):
    """Parse all games in directory and write to CSV."""
    html_files = sorted(glob(os.path.join(input_dir, "*.html")), 
                       key=lambda x: int(os.path.basename(x).replace('.html', '')))
    
    if not html_files:
        print(f"No HTML files found in {input_dir}", file=sys.stderr)
        return
    
    print(f"Found {len(html_files)} game files to parse", file=sys.stderr)
    print(f"Writing to {output_file}", file=sys.stderr)
    
    with open(output_file, 'w', encoding='utf-8') as out:
        # Write header
        out.write("gid || airdate || rnd || category || value || text || answer\n")
        
        clue_count = 0
        for i, filepath in enumerate(html_files, 1):
            if i % 100 == 0:
                print(f"Parsed {i}/{len(html_files)} games ({clue_count} clues so far)...", file=sys.stderr)
            
            clues = parse_game(filepath)
            for clue in clues:
                out.write(format_clue(clue) + "\n")
                clue_count += 1
        
        print(f"Done! Parsed {len(html_files)} games with {clue_count} total clues", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python parse_and_create_csv.py <input_dir> <output_csv>")
        print("Example: python parse_and_create_csv.py new_games_2024 jarchive_new.csv")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_file = sys.argv[2]
    
    main(input_dir, output_file)
