#!/bin/bash
set -e
cd $(dirname "$0")/..

x=`cat $PWD/last_episode.txt`
start=$(($x+1))

# Create directory if it doesn't exist
mkdir -p $PWD/new_games

python3 $PWD/download.py $PWD/new_games $start
python3 $PWD/parser.py -d $PWD/new_games > $PWD/jarchive_tmp.csv

# Only update if we have new data
if [ -s $PWD/jarchive_tmp.csv ]; then
    cat $PWD/jarchive_tmp.csv >> $PWD/jarchive.csv
fi

# Update last_episode.txt if HTML files were downloaded
if ls $PWD/new_games/*.html 1> /dev/null 2>&1; then
    ls -1 $PWD/new_games/*.html | tail -n 1 | egrep -o '[0-9]+' > $PWD/last_episode.txt
    rm $PWD/new_games/*.html
fi

# Clean up temp file if it exists
if [ -f $PWD/jarchive_tmp.csv ]; then
    rm $PWD/jarchive_tmp.csv
fi
