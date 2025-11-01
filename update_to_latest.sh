#!/bin/bash
set -e

START=7291
END=9425

cd "$(dirname "$0")"

for ((ep=$START; ep<=$END; ep++)); do
    echo "Processing episode $ep"
    python3 download.py new_games $ep
    python3 parser.py -d new_games > jarchive_tmp.csv
    cat jarchive_tmp.csv >> jarchive.csv
    echo $ep > last_episode.txt
    rm -f new_games/*.html jarchive_tmp.csv
done

echo "Update complete. Last episode: $END"
