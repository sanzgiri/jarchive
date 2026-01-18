#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Download new Jeopardy episodes and create a CSV that can be appended to jarchive_2023.csv
"""

import os
import sys
import time
from urllib.request import urlopen
from urllib.error import HTTPError
import concurrent.futures as futures

SECONDS_BETWEEN_REQUESTS = 2  # Reduced from 5 to speed up
ERROR_MSG = b"ERROR: No game"
NUM_THREADS = 10  # Balanced threading

def download_page(game_id):
    """Download a single game page."""
    url = f'http://j-archive.com/showgame.php?game_id={game_id}'
    try:
        response = urlopen(url)
        if response.code == 200:
            return response.read()
        else:
            print(f"Invalid response for game {game_id}")
            return None
    except HTTPError as e:
        print(f"HTTP error for game {game_id}: {e}")
        return None
    except Exception as e:
        print(f"Error downloading game {game_id}: {e}")
        return None

def download_and_save(game_id, output_dir):
    """Download and save a game, return True if successful."""
    filepath = os.path.join(output_dir, f"{game_id}.html")
    
    # Skip if already downloaded
    if os.path.exists(filepath):
        return True
    
    html = download_page(game_id)
    
    if html is None:
        return False
    
    if ERROR_MSG in html:
        print(f"Game {game_id} does not exist (reached end)")
        return False
    
    # Save the file
    try:
        with open(filepath, 'wb') as f:
            f.write(html)
        print(f"Downloaded game {game_id}")
        time.sleep(SECONDS_BETWEEN_REQUESTS)
        return True
    except IOError as e:
        print(f"Error saving game {game_id}: {e}")
        return False

def download_range(start_id, end_id, output_dir):
    """Download a range of games."""
    os.makedirs(output_dir, exist_ok=True)

    # First, probe to find the actual end
    print(f"Probing for latest episode starting from {start_id}...")
    actual_end = find_last_available(start_id, end_id)

    if actual_end < start_id:
        print(f"No new episodes found. Archive is up to date at episode {start_id - 1}.")
        return 0, []

    total = actual_end - start_id + 1
    completed = 0
    failed = []

    print(f"Downloading games {start_id} to {actual_end} ({total} total)")
    print(f"Using {NUM_THREADS} threads with {SECONDS_BETWEEN_REQUESTS}s delay")
    print(f"Estimated time: ~{(total * SECONDS_BETWEEN_REQUESTS) / (NUM_THREADS * 60):.1f} minutes")
    print("-" * 60)

    with futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        # Submit all jobs
        future_to_id = {
            executor.submit(download_and_save, gid, output_dir): gid
            for gid in range(start_id, actual_end + 1)
        }

        # Process as they complete
        for future in futures.as_completed(future_to_id):
            game_id = future_to_id[future]
            try:
                success = future.result()
                if success:
                    completed += 1
                else:
                    failed.append(game_id)

                if completed > 0 and completed % 50 == 0:
                    print(f"Progress: {completed}/{total} completed ({completed/total*100:.1f}%)")
            except Exception as e:
                print(f"Exception for game {game_id}: {e}")
                failed.append(game_id)

    print("-" * 60)
    print(f"Download complete!")
    print(f"Successfully downloaded: {completed}")
    print(f"Failed: {len(failed)}")
    if failed:
        print(f"Failed game IDs: {failed[:10]}{'...' if len(failed) > 10 else ''}")

    return completed, failed

def find_last_available(start_id, max_id):
    """Find the last available episode using binary search-like probing."""
    # First check if start_id exists
    if not check_game_exists(start_id):
        return start_id - 1

    # Do a quick probe forward to find approximate end
    probe = start_id
    step = 50

    while probe <= max_id:
        if check_game_exists(probe):
            probe += step
        else:
            # Found a gap, search backward
            break

    # Now find exact end by checking backwards
    end = probe - step
    for i in range(probe - 1, end, -1):
        if check_game_exists(i):
            return i

    return end

def check_game_exists(game_id):
    """Quick check if a game exists without downloading."""
    url = f'http://j-archive.com/showgame.php?game_id={game_id}'
    try:
        response = urlopen(url)
        if response.code == 200:
            html = response.read()
            return ERROR_MSG not in html
    except:
        pass
    return False

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python download_new_episodes.py <output_dir> <start_id> <end_id>")
        print("Example: python download_new_episodes.py new_games_2024 7291 9425")
        sys.exit(1)
    
    output_dir = sys.argv[1]
    start_id = int(sys.argv[2])
    end_id = int(sys.argv[3])
    
    download_range(start_id, end_id, output_dir)
