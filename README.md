# jarchive

[![Update Jarchive Weekly](https://github.com/sanzgiri/jarchive/actions/workflows/update_jarchive.yml/badge.svg)](https://github.com/sanzgiri/jarchive/actions/workflows/update_jarchive.yml)

A comprehensive Jeopardy! clue database scraped from [j-archive.com](https://j-archive.com), updated weekly via GitHub Actions.

## Data

- **File:** `jarchive.csv` — pipe-delimited (`||`) with columns: `gid`, `airdate`, `rnd`, `category`, `value`, `text`, `answer`
- **Coverage:** Episodes 1–9,479 (586,757 clues, 9,471 unique episodes)
- **Missing episodes:** 9161, 9165, 9172, 9181, 9319, 9448, 9450, 9452 (not available on j-archive)
- **Empty answers:** ~178 clues (0.03%) where j-archive doesn't provide the response

## Automatic Updates

The archive updates every **Saturday at 3:00 PM UTC** via the `update_jarchive.yml` workflow:

1. Downloads new episodes from j-archive.com (HTTPS)
2. Parses clues and answers from the HTML
3. Appends to `jarchive.csv`, sorted by game ID
4. Commits and pushes the updated file

You can also trigger a manual update from the Actions tab.

## Scripts

| Script | Purpose |
|--------|---------|
| `download_new_episodes.py` | Downloads game HTML files from j-archive.com |
| `parse_and_create_csv.py` | Parses HTML into CSV (supports both old and new j-archive formats) |
| `parser.py` | Legacy parser (also updated for new format) |
| `backfill_answers.py` | Re-downloads episodes to fill in missing answers |
| `test_parser.py` | Tests parser against both HTML formats |

## Running Locally

```bash
pip install beautifulsoup4 lxml

# Parse existing HTML files
python3 parse_and_create_csv.py <html_dir> <output.csv>

# Download new episodes
python3 download_new_episodes.py <output_dir> <start_id> <end_id>

# Backfill missing answers (re-downloads from j-archive)
python3 backfill_answers.py --dry-run        # preview
python3 backfill_answers.py --batch-size 25  # run
```

## Credits

Derived from: https://github.com/whymarrh/jeopardy-parser
