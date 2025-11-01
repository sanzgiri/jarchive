# Jarchive Update - November 2025

## Summary of Changes

This update modernizes the jarchive dataset and automates weekly updates via GitHub Actions.

### Data Updates
- ✅ Downloaded episodes 7291-9302 (2,012 new games)
- ✅ Recovered 9 previously missing episodes (349, 1478, 2681, 2815, 3303, 3503, 4230, 5997, 6704)
- ✅ Sorted entire dataset by game ID
- ✅ Updated jarchive.csv (regular git file, 83MB)

### Final Statistics
- **Total Clues**: 576,253
- **Unique Games**: 9,298 (out of 9,302 total IDs)
- **Game ID Range**: 1 to 9,302
- **Date Range**: 1997-04-10 to 2025-10-31
- **Missing Games**: 4 (Celebrity Jeopardy episodes not yet transcribed: 9161, 9165, 9172, 9181)

## New Files Added

### Scripts
1. **`download_new_episodes.py`** - Improved parallel downloader with progress tracking
2. **`parse_and_create_csv.py`** - Enhanced parser with better error handling
3. **`_action_files/update_jarchive.sh`** - Main automation script for weekly updates

### Documentation
4. **`UPDATE_PROCESS.md`** - Comprehensive documentation covering:
   - Update process (automated and manual)
   - File structure and formats
   - GitHub Actions workflow
   - Git LFS setup
   - Troubleshooting guide

### GitHub Actions
5. **`.github/workflows/update_jarchive.yml`** - Weekly automation workflow
   - Runs every Saturday at 3:00 PM UTC
   - Handles Git LFS properly
   - Can be manually triggered

## Modified Files

### Configuration
- **`.gitignore`** - Added jarchive-specific exclusions for temporary files
- **`last_episode.txt`** - Updated from 7290 to 9302

### Data
- **`jarchive.csv`** - Updated and sorted dataset (Git LFS)
  - Previous: ~456,524 clues (games 1-7290)
  - Current: 576,253 clues (games 1-9302)
  - Added: 119,729 new clues

## GitHub Actions Workflow

### Schedule
- **Automated**: Every Saturday at 3:00 PM UTC
- **Manual**: Can be triggered via GitHub Actions UI

### Process Flow
1. Checkout repository
2. Install Python dependencies (beautifulsoup4, lxml)
3. Run update script:
   - Download new episodes from j-archive.com
   - Parse HTML to CSV format
   - Merge and sort with existing data
   - Update last_episode.txt
4. Commit and push changes (if any)

### Monitoring
- Check GitHub Actions tab for execution logs
- Commit messages include episode count and statistics
- Automatic error notifications via GitHub

## Local Development Setup

```bash
# Clone repository
git clone https://github.com/sanzgiri/jarchive.git
cd jarchive

# Create virtual environment with uv
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install beautifulsoup4 lxml
```

## Manual Update Process

To manually trigger an update:

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Run update script
bash _action_files/update_jarchive.sh

# 3. Commit and push
git add jarchive.csv last_episode.txt
git commit -m "Manual update to episode $(cat last_episode.txt)"
git push
```

## Technical Improvements

### Download Process
- Parallel downloading with 10 threads
- Reduced delay (2s vs 5s) for faster updates
- Better progress tracking and error handling
- Automatic retry capability

### Parsing
- Improved error handling for malformed HTML
- Better handling of special episodes (Celebrity Jeopardy, etc.)
- Sorted output by game ID

### Automation
- Robust merge and sort process
- Automatic duplicate detection
- Clean temporary file management

## Known Issues

### Celebrity Jeopardy Episodes
Four recent Celebrity Jeopardy episodes (9161, 9165, 9172, 9181) exist on j-archive.com but haven't been transcribed yet. They will be automatically added when transcription is complete.

### Legacy Files
The following legacy files are still present but not used by the new workflow:
- `download.py` (replaced by `download_new_episodes.py`)
- `parser.py` (replaced by `parse_and_create_csv.py`)
- `_action_files/get_new_games.sh` (replaced by `update_jarchive.sh`)

These are kept for backwards compatibility but can be removed in a future update.

## Future Enhancements

### Potential Improvements
1. **Database conversion**: Convert CSV to SQLite/PostgreSQL for better querying
2. **API layer**: Create REST API for programmatic access
3. **Data validation**: Add automated testing for data quality
4. **Statistics dashboard**: Generate weekly statistics reports
5. **Missing episode monitor**: Alert when missing episodes become available

### Maintenance Tasks
- Monthly check for missing episodes
- Annual dependency updates
- Quarterly backup verification

## Credits

- Original jarchive data collection by the J! Archive community
- Automation improvements: November 2025
- Data source: http://j-archive.com

## Resources

- **Repository**: https://github.com/sanzgiri/jarchive
- **J! Archive**: http://j-archive.com
- **Git LFS**: https://git-lfs.github.com
- **Documentation**: UPDATE_PROCESS.md

---

Last Updated: November 1, 2025
