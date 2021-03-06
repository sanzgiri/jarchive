#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

import itertools
import os
from urllib.request import urlopen
from urllib.error import HTTPError
import time
import concurrent.futures as futures  
import sys

SECONDS_BETWEEN_REQUESTS = 5
ERROR_MSG = b"ERROR: No game"
NUM_THREADS = 2  # Be conservative
try:
    import multiprocessing
    # Since it's a lot of IO let's double # of actual cores
    NUM_THREADS = multiprocessing.cpu_count() * 2
    print(f"Using {NUM_THREADS} threads")
except (ImportError, NotImplementedError):
    pass

def create_archive(adir, start):

    current_working_directory = os.path.dirname(os.path.abspath(__file__))
    archive_folder = os.path.join(current_working_directory, adir)
    if not os.path.isdir(archive_folder):
        print(f"Making {archive_folder}")
        os.mkdir(archive_folder)

    print("Downloading game files")
    download_pages(start, archive_folder)


def download_pages(start, archive_folder):
    page = start
    with futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        # We submit NUM_THREADS tasks at a time since we don't know how many
        # pages we will need to download in advance
        while True:
            l = []
            for i in range(NUM_THREADS):
                f = executor.submit(download_and_save_page, page, archive_folder)
                l.append(f)
                page += 1
            # Block and stop if we're done downloading the page
            if not all(f.result() for f in l):
                break


def download_and_save_page(page, archive_folder):
    new_file_name = "%s.html" % page
    destination_file_path = os.path.join(archive_folder, new_file_name)
    if not os.path.exists(destination_file_path):
        html = download_page(page)
        if ERROR_MSG in html:
            # Now we stop
            print("Finished downloading. Now parse.")
            return False
        elif html:
            save_file(html, destination_file_path)
            time.sleep(SECONDS_BETWEEN_REQUESTS)  # Remember to be kind to the server
    else:
        print(f"Already downloaded {destination_file_path}")
    return True


def download_page(page):
    url = 'http://j-archive.com/showgame.php?game_id=%s' % page
    html = None
    try:
        response = urlopen(url)
        if response.code == 200:
            print(f"Downloading {url}")
            html = response.read()
        else:
            print(f"Invalid URL: {url}")
    except HTTPError:
        print(f"failed to open{url}")
    return html


def save_file(html, filename):
    try:
        with open(filename, 'wb') as f:
            f.write(html)
    except IOError:
        print(f"Couldn't write to file {filename}")


if __name__ == "__main__":

    # directory to store game files
    adir = sys.argv[1]
    # starting game to download
    start = int(sys.argv[2])

    create_archive(adir, start)
