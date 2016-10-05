# About

This program helps you to download songs from a list. 

# Installation

Before first usage make sure you have the requirements installed:

`sudo pip install -r requirements.txt`

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

# Authors

The program is written by Antun Razum and Mislav Magerl.
