#!/usr/bin/env python3
"""
Test the parser against both old and new j-archive HTML formats.
Run: python3 test_parser.py
"""

import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_and_create_csv import parse_game

# Old format: onmouseover with <em class="correct_response">
OLD_FORMAT_HTML = '''<html><head><title>J! Archive - Show #100, aired 2021-01-15</title></head><body>
<div id="jeopardy_round">
<table><tr>
<td class="category_name">HISTORY</td>
<td class="category_name">SCIENCE</td>
<td class="category_name">MOVIES</td>
<td class="category_name">FOOD</td>
<td class="category_name">SPORTS</td>
<td class="category_name">MUSIC</td>
</tr></table>
<table><tr>
<td class="clue">
<table><tr><td class="clue_value">$200</td></tr>
<tr><td class="clue_text" id="clue_J_1_1">This president was inaugurated in 1961</td></tr></table>
<div onmouseover="toggle('clue_J_1_1', 'clue_J_1_1_stuck', '<em class=&quot;correct_response&quot;>Kennedy</em>')" onmouseout="toggle('clue_J_1_1', 'clue_J_1_1_stuck')"></div>
</td>
<td class="clue">
<table><tr><td class="clue_value">$200</td></tr>
<tr><td class="clue_text" id="clue_J_2_1">H2O is the formula for this</td></tr></table>
<div onmouseover="toggle('clue_J_2_1', 'clue_J_2_1_stuck', '<em class=&quot;correct_response&quot;>water</em>')" onmouseout="toggle('clue_J_2_1', 'clue_J_2_1_stuck')"></div>
</td>
<td class="clue"></td><td class="clue"></td><td class="clue"></td><td class="clue"></td>
</tr></table>
</div>
<table class="final_round">
<tr><td class="category_name">GEOGRAPHY</td></tr>
<tr><td class="clue_text" id="clue_FJ">The largest continent</td></tr>
<div onmouseover="toggle('clue_FJ', 'clue_FJ_stuck', '<em>Asia</em>')" onmouseout="toggle('clue_FJ', 'clue_FJ_stuck')"></div>
</table>
</body></html>'''

# New format: hidden div with id="clue_X_correct_response"
NEW_FORMAT_HTML = '''<html><head><title>J! Archive - Show #9400, aired 2025-03-15</title></head><body>
<div id="jeopardy_round">
<table><tr>
<td class="category_name">HISTORY</td>
<td class="category_name">SCIENCE</td>
<td class="category_name">MOVIES</td>
<td class="category_name">FOOD</td>
<td class="category_name">SPORTS</td>
<td class="category_name">MUSIC</td>
</tr></table>
<table><tr>
<td class="clue" id="clue_J_1_1">
<table><tr><td class="clue_value">$200</td></tr>
<tr><td class="clue_text" id="clue_J_1_1_stuck">This president was inaugurated in 2021</td></tr></table>
<div id="clue_J_1_1_correct_response" style="display:none;">Biden</div>
</td>
<td class="clue" id="clue_J_2_1">
<table><tr><td class="clue_value">$200</td></tr>
<tr><td class="clue_text" id="clue_J_2_1_stuck">The chemical symbol Fe represents this element</td></tr></table>
<div id="clue_J_2_1_correct_response" style="display:none;">iron</div>
</td>
<td class="clue"></td><td class="clue"></td><td class="clue"></td><td class="clue"></td>
</tr></table>
</div>
<div id="double_jeopardy_round">
<table><tr>
<td class="category_name">WORLD LEADERS</td>
<td class="category_name">LITERATURE</td>
<td class="category_name">SCIENCE</td>
<td class="category_name">ART</td>
<td class="category_name">GEOGRAPHY</td>
<td class="category_name">POP CULTURE</td>
</tr></table>
<table><tr>
<td class="clue" id="clue_DJ_1_1">
<table><tr><td class="clue_value_daily_double">Daily Double: $2,000</td></tr>
<tr><td class="clue_text" id="clue_DJ_1_1_stuck">This French leader was exiled to Elba</td></tr></table>
<div id="clue_DJ_1_1_correct_response" style="display:none;">Napoleon</div>
</td>
<td class="clue"></td><td class="clue"></td><td class="clue"></td><td class="clue"></td><td class="clue"></td>
</tr></table>
</div>
<table class="final_round">
<tr><td class="category_name">U.S. PRESIDENTS</td></tr>
<tr><td class="clue_text" id="clue_FJ">The only president to serve non-consecutive terms</td></tr>
<div id="clue_FJ_correct_response" style="display:none;">Grover Cleveland</div>
</table>
</body></html>'''

# Edge case: answer with special characters
SPECIAL_CHARS_HTML = '''<html><head><title>J! Archive - Show #9450, aired 2025-05-01</title></head><body>
<div id="jeopardy_round">
<table><tr>
<td class="category_name">BEFORE &amp; AFTER</td>
<td class="category_name">CAT2</td>
<td class="category_name">CAT3</td>
<td class="category_name">CAT4</td>
<td class="category_name">CAT5</td>
<td class="category_name">CAT6</td>
</tr></table>
<table><tr>
<td class="clue" id="clue_J_1_1">
<table><tr><td class="clue_value">$200</td></tr>
<tr><td class="clue_text" id="clue_J_1_1_stuck">This &quot;Rock &amp; Roll&quot; hall of famer sang &quot;Purple Rain&quot;</td></tr></table>
<div id="clue_J_1_1_correct_response" style="display:none;">Prince</div>
</td>
<td class="clue"></td><td class="clue"></td><td class="clue"></td><td class="clue"></td><td class="clue"></td>
</tr></table>
</div>
<table class="final_round">
<tr><td class="category_name">MATH</td></tr>
<tr><td class="clue_text" id="clue_FJ">This number is both the square of 12 &amp; a gross</td></tr>
<div id="clue_FJ_correct_response" style="display:none;">144</div>
</table>
</body></html>'''


def run_tests():
    """Run all parser tests."""
    passed = 0
    failed = 0

    def assert_eq(test_name, actual, expected):
        nonlocal passed, failed
        if actual == expected:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {test_name}")
            print(f"    Expected: {expected}")
            print(f"    Got:      {actual}")

    # Write test HTML to temp files
    with tempfile.TemporaryDirectory() as tmpdir:
        old_path = os.path.join(tmpdir, "100.html")
        new_path = os.path.join(tmpdir, "9400.html")
        special_path = os.path.join(tmpdir, "9450.html")

        with open(old_path, 'w') as f:
            f.write(OLD_FORMAT_HTML)
        with open(new_path, 'w') as f:
            f.write(NEW_FORMAT_HTML)
        with open(special_path, 'w') as f:
            f.write(SPECIAL_CHARS_HTML)

        # Test 1: Old format
        print("Test 1: Old format (pre-2022 onmouseover)")
        clues = parse_game(old_path)
        assert_eq("old format clue count", len(clues), 3)
        assert_eq("old format answer 1", clues[0][6], "Kennedy")
        assert_eq("old format answer 2", clues[1][6], "water")
        assert_eq("old format FJ answer", clues[2][6], "Asia")
        assert_eq("old format round 1", clues[0][2], 1)
        assert_eq("old format FJ round", clues[2][2], 3)

        # Test 2: New format
        print("Test 2: New format (2022+ hidden div)")
        clues = parse_game(new_path)
        assert_eq("new format clue count", len(clues), 4)
        assert_eq("new format answer J1", clues[0][6], "Biden")
        assert_eq("new format answer J2", clues[1][6], "iron")
        assert_eq("new format answer DJ", clues[2][6], "Napoleon")
        assert_eq("new format FJ answer", clues[3][6], "Grover Cleveland")
        assert_eq("new format round DJ", clues[2][2], 2)

        # Test 3: No empty answers
        print("Test 3: No empty answers in new format")
        empty_answers = [c for c in clues if not c[6]]
        assert_eq("no empty answers", len(empty_answers), 0)

        # Test 4: Special characters
        print("Test 4: Special characters in clues/answers")
        clues = parse_game(special_path)
        assert_eq("special chars clue count", len(clues), 2)
        assert_eq("special chars answer", clues[0][6], "Prince")
        assert_eq("special chars FJ answer", clues[1][6], "144")

        # Test 5: Game IDs extracted from filename
        print("Test 5: Game ID extraction")
        clues = parse_game(new_path)
        assert_eq("game id from filename", clues[0][0], 9400)

    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
