# Jarchive Update Process

This document describes the automated update process for maintaining the Jeopardy! Archive dataset.

## Overview

The jarchive dataset is automatically updated weekly via GitHub Actions to download, parse, and append new Jeopardy! episodes to `jarchive.csv`.

## Files Structure

### Main Data Files
- **`jarchive.csv`** - Main archive file (stored in Git LFS)
  - Contains all Jeopardy! clues from episode 1 to the latest
  - Sorted by game ID (gid)
  - Uses `||` as field separator
  - Currently: 576,253 clues from 9,298 games (as of Nov 1, 2025)

- **`jarchive_2023.csv`** - Local working copy (not tracked in git)
- **`jarchive_2023_backup.csv`** - Local backup (not tracked in git)

### Episode Tracking
- **`last_episode.txt`** - Contains the highest game ID in the archive
  - Used by automation to determine where to start downloading

### Scripts

#### Download Scripts
- **`download_new_episodes.py`** - Improved parallel downloader
  - Downloads episodes from j-archive.com
  - Progress tracking and error handling
  - Configurable threading and delays

- **`download.py`** - Original downloader (legacy)

#### Parsing Scripts
- **`parse_and_create_csv.py`** - Parse HTML files to CSV
  - Extracts clues from downloaded HTML
  - Handles all three rounds (Jeopardy, Double Jeopardy, Final Jeopardy)
  - Outputs CSV with `||` separator

- **`parser.py`** - Original parser (legacy)

#### Automation Scripts
- **`_action_files/update_jarchive.sh`** - Main update script
  - Downloads new episodes since last update
  - Parses HTML to CSV
  - Merges and sorts with existing data
  - Updates last_episode.txt
  - Cleans up temporary files

- **`_action_files/get_new_games.sh`** - Legacy update script

### GitHub Actions
- **`.github/workflows/update_jarchive.yml`** - Weekly automation
  - Runs every Saturday at 3:00 PM UTC
  - Can be manually triggered
  - Handles Git LFS properly

## CSV Format

```
gid || airdate || rnd || category || value || text || answer
```

**Fields:**
- `gid`: Game ID (integer)
- `airdate`: Air date (YYYY-MM-DD)
- `rnd`: Round number (1=Jeopardy, 2=Double Jeopardy, 3=Final Jeopardy)
- `category`: Category name
- `value`: Dollar value (or "False" for Final Jeopardy)
- `text`: Clue text
- `answer`: Correct answer/response

## Update Process

### Automated (Weekly)

1. **Trigger**: Every Saturday at 3:00 PM UTC
2. **Download**: Fetch episodes from `last_episode.txt + 1` to latest
3. **Parse**: Extract clues from HTML files
4. **Merge**: Append new clues to jarchive.csv
5. **Sort**: Sort entire file by game ID
6. **Commit**: Push updated files to GitHub (via Git LFS)

### Manual Update

To manually update the archive:

```bash
# 1. Ensure uv environment is set up
uv venv
source .venv/bin/activate
uv pip install beautifulsoup4 lxml

# 2. Run the update script
bash _action_files/update_jarchive.sh

# 3. Verify changes
git status
git diff last_episode.txt

# 4. Commit and push
git add jarchive.csv last_episode.txt
git commit -m "Manual update to episode $(cat last_episode.txt)"
git push
```

## Git LFS Setup

The `jarchive.csv` file is tracked with Git LFS due to its size (83MB+).

### Configuration
`.gitattributes`:
```
jarchive.csv filter=lfs diff=lfs merge=lfs -text
```

### Working with LFS

```bash
# Install Git LFS (one time)
git lfs install

# Pull LFS files
git lfs pull

# Check LFS status
git lfs ls-files

# Track new large file
git lfs track "*.csv"
```

## Missing Episodes

As of November 1, 2025, there are 4 missing episodes:
- **9161, 9165, 9172, 9181**: Celebrity Jeopardy episodes that haven't been fully transcribed on j-archive.com yet

These will be automatically added once they become available on the source website.

## GitHub Actions Workflow

### Workflow File
`.github/workflows/update_jarchive.yml`

### Trigger Options
1. **Scheduled**: Every Saturday at 3:00 PM UTC
2. **Manual**: Via GitHub Actions UI (workflow_dispatch)

### Steps
1. Checkout repository with LFS
2. Set up Python 3.11
3. Install dependencies (beautifulsoup4, lxml)
4. Pull latest jarchive.csv from LFS
5. Run update script
6. Commit and push if changes exist

### Monitoring
- Check GitHub Actions tab for run history
- View logs for any errors
- Commit messages show episode count and stats

## Environment Setup

### Local Development

```bash
# Clone repository
git clone https://github.com/sanzgiri/jarchive.git
cd jarchive

# Set up Git LFS
git lfs install
git lfs pull

# Create virtual environment
uv venv
source .venv/bin/activate  # or `source .venv/bin/activate` on Windows

# Install dependencies
uv pip install beautifulsoup4 lxml
```

### Dependencies
- **Python 3.11+**
- **beautifulsoup4**: HTML parsing
- **lxml**: XML/HTML parser backend
- **Git LFS**: Large file storage

## Troubleshooting

### Issue: jarchive.csv not updating
**Solution**: Check if Git LFS is installed and configured properly
```bash
git lfs install
git lfs pull
```

### Issue: GitHub Action fails
**Solution**: 
1. Check logs in GitHub Actions tab
2. Verify last_episode.txt is valid
3. Ensure dependencies are installed correctly

### Issue: Duplicate episodes
**Solution**: The merge script sorts and deduplicates by game ID automatically

### Issue: Missing episodes
**Solution**: 
1. Check if episodes exist on j-archive.com
2. Manually download missing episodes (see Manual Update section)
3. Some Celebrity Jeopardy episodes may not be transcribed yet

## Maintenance

### Regular Tasks
- Monitor GitHub Actions runs weekly
- Check for new missing episodes monthly
- Update dependencies annually

### Data Quality
- CSV is always sorted by game ID
- Duplicates are handled during merge
- Failed downloads are logged and can be retried

## Statistics (as of Nov 1, 2025)

- **Total Clues**: 576,253
- **Unique Games**: 9,298
- **Game ID Range**: 1 to 9,302
- **Missing Games**: 4 (Celebrity Jeopardy episodes)
- **Date Range**: 1997-04-10 to 2025-10-31
- **File Size**: ~83MB

## References

- J! Archive: http://j-archive.com
- GitHub Repository: https://github.com/sanzgiri/jarchive
- Git LFS Documentation: https://git-lfs.github.com
