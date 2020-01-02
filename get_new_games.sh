#!/bin/bash

x=`cat $PWD/last_episode.txt`
start=$(($x+1))
/home/ubuntu/anaconda2/envs/jarchive/bin/python download.py $PWD/new_games 6507
/home/ubuntu/anaconda2/envs/jarchive/bin/python parser.py -d $PWD/new_games > $PWD/jarchive_tmp.csv
cat $PWD/jarchive_tmp.csv >> $PWD/jarchive.csv
ls -1 $PWD/new_games/*.html | tail -n 1 | egrep -o '[0-9]+' > $PWD/last_episode.txt
rm $PWD/new_games/*.html $PWD/jarchive_tmp.csv
