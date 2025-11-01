#!/bin/bash
# Update jarchive.csv with new episodes
# This script downloads new games, parses them, sorts, and appends to jarchive.csv

set -e
cd $(dirname "$0")/..

echo "=== Starting jarchive update ==="

# Read the last episode number
LAST_EPISODE=$(cat "$PWD/last_episode.txt")
START_EPISODE=$((LAST_EPISODE + 1))

echo "Last episode in archive: $LAST_EPISODE"
echo "Starting download from: $START_EPISODE"

# Create temporary directory for new games
TEMP_DIR="$PWD/temp_new_games"
mkdir -p "$TEMP_DIR"

# Download new episodes
echo "=== Downloading new episodes ==="
python3 "$PWD/download_new_episodes.py" "$TEMP_DIR" "$START_EPISODE" 9999

# Check if any files were downloaded
NUM_FILES=$(ls -1 "$TEMP_DIR"/*.html 2>/dev/null | wc -l | tr -d ' ')

if [ "$NUM_FILES" -eq "0" ]; then
    echo "No new episodes found. Archive is up to date."
    rm -rf "$TEMP_DIR"
    exit 0
fi

echo "Downloaded $NUM_FILES new game files"

# Parse the new games
echo "=== Parsing new games ==="
python3 "$PWD/parse_and_create_csv.py" "$TEMP_DIR" "$PWD/jarchive_new_temp.csv"

# Get the count of new clues
NEW_CLUES=$(tail -n +2 "$PWD/jarchive_new_temp.csv" | wc -l | tr -d ' ')
echo "Parsed $NEW_CLUES new clues"

if [ "$NEW_CLUES" -eq "0" ]; then
    echo "No valid clues found in new episodes."
    rm -rf "$TEMP_DIR" "$PWD/jarchive_new_temp.csv"
    exit 0
fi

# Append and sort
echo "=== Merging and sorting ==="
python3 << 'PYTHON_SCRIPT'
import sys

print("Reading existing jarchive.csv...")
rows = []
with open('jarchive.csv', 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        fields = [field.strip() for field in line.strip().split('||')]
        if len(fields) >= 7:
            rows.append(fields)

existing_count = len(rows)
print(f"Existing clues: {existing_count}")

# Read new clues
print("Reading new clues...")
with open('jarchive_new_temp.csv', 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        fields = [field.strip() for field in line.strip().split('||')]
        if len(fields) >= 7:
            rows.append(fields)

new_count = len(rows) - existing_count
print(f"Added {new_count} new clues")

# Sort by gid
print("Sorting by game ID...")
rows.sort(key=lambda x: int(x[0]) if x[0].isdigit() else 0)

# Write sorted file
print("Writing sorted jarchive.csv...")
with open('jarchive.csv', 'w', encoding='utf-8') as f:
    f.write("gid || airdate || rnd || category || value || text || answer\n")
    for row in rows:
        f.write(" || ".join(row) + "\n")

# Get stats
unique_gids = len(set(int(row[0]) for row in rows if row[0].isdigit()))
max_gid = max(int(row[0]) for row in rows if row[0].isdigit())
print(f"Total clues: {len(rows):,}")
print(f"Unique games: {unique_gids}")
print(f"Max game ID: {max_gid}")

# Update last_episode.txt
with open('last_episode.txt', 'w') as f:
    f.write(str(max_gid))
print(f"Updated last_episode.txt to {max_gid}")
PYTHON_SCRIPT

# Clean up
echo "=== Cleaning up ==="
rm -rf "$TEMP_DIR" "$PWD/jarchive_new_temp.csv"

echo "=== Update complete! ==="
