# About

This program helps you to download songs from a list. 

# Installation

Before first usage make sure you have the requirements installed:

`sudo pip install -r requirements.txt`

Note: If you have trouble installing pycurl check [this](http://stackoverflow.com/a/30590000) answer. 

# Usage

Write all of your favourite songs in a file line by line. You can take youtube_id of the song and write it like `#<youtube_id>`.

The program searches Youtube and takes the first search query as the song and downloads it. 

You can find arguments with `./pjesme.py -h`.


# Example

Create a file songs.txt. Write all of your favourite songs:

```
Toto - Africa
#ws2WmhwKcx8
Petar Graso - Srce za vodica
```

and run `./pjesme.py songs.txt -o songs` and the program will download your songs to songs/ directory.


Also, we included a file which includes a lot of compilations of best classical music. You can download it by writing `./pjesme.py lists/classic.txt -o classic-music-folder`

# Authors

The program is written by Antun Razum and Mislav Magerl.
