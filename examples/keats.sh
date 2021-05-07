#!/bin/sh

cd ~/path/to/keats_downloader

# source venv/bin/activate

python 1_list_videos.py
python 2_check_exists.py
python 3_save.py
