
> :warning: This project is very WIP, I provide no warranty. Depending on how your lecturer uses KEATS, the link to the video page or the video itself might not be recognised.

# Keats Downloader
This is a project intended to automatically download all videos in a course and store them locally. Benefits include:
- Being able to playback videos at non-turtle speed (more than 2x)
- Being able to use subtitles as a semi-accurate transcript
- Being able to watch high-resolution video streams with no buffering

## Requirements
1. To install the python modules used by the project run the following in the directory. 
```
pip install -r requirements.txt
```


2. Install FFMpeg through your distribution's package manager or download it [here](https://github.com/BtbN/FFmpeg-Builds/releases) and copy the contents of the bin folder so that there are 3 files in the main directory.

```
./ffmpeg.exe
./ffplay.exe
./ffprobe.exe
```

3. (Optional) If your chrome/chromium build is not on the stable version, select your major version from [here](https://pypi.org/project/chromedriver-py/#history) and execute:
```
pip install chromedriver-py==<version>
```

## Basic usage
1. Create a `courses.txt` file with your course urls to download videos from, separated by newlines. Its contents should look something like this:
```
https://keats.kcl.ac.uk/course/view.php?id=AAAAA
https://keats.kcl.ac.uk/course/view.php?id=BBBBB
https://keats.kcl.ac.uk/course/view.php?id=CCCCC
https://keats.kcl.ac.uk/course/view.php?id=DDDDD
```
2. Execute the python files in their numbered order and optionally create a script ([examples](https://github.com/dylantjb/keats_downloader/examples)). The 0-numbered files should only be executed once, others will have to be repeated if you want to download new videos. `0_login.py` gives you an opportunity to login to your Keats account because the browser uses a separate profile.
