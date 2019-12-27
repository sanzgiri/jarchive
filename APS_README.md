
* Cloned from git://github.com/whymarrh/jeopardy-parser.git
* Original has been modified to not write to sql db and use '||' as a separator
* This allows easier loading into a pandas dataframe for subsequent cleaning

```
pip install -r requirements.txt
python download.py <archive_dir> <starting_game_to_download>
python parser.py -d <archive_dir> > jarchive_xxx.csv
cat jarchive_xxx.csv > jarchive.csv
```

* This first downloads the games into directory j-archive (currently has games upto id 6095, which is 7/27/18)
* parser.py then extracts questions to jarchive.csv


