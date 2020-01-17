#!/bin/bash

DIR="/home/ubuntu/jarchive"
x=`cat $DIR/last_episode.txt`
start=$(($x+1))
/home/ubuntu/anaconda2/envs/jarchive/bin/python $DIR/download.py $DIR/new_games $start
/home/ubuntu/anaconda2/envs/jarchive/bin/python $DIR/parser.py -d $DIR/new_games > $DIR/jarchive_tmp.csv
cat $DIR/jarchive_tmp.csv >> $DIR/jarchive.csv
ls -1 $DIR/new_games/*.html | tail -n 1 | egrep -o '[0-9]+' > $DIR/last_episode.txt
rm $DIR/new_games/*.html $DIR/jarchive_tmp.csv
