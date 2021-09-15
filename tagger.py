from os import path
from pydub import AudioSegment
import eyed3


def tag(fileName : str, oldExt, title, artist, album):

    if not path.exists(f"./audio/{fileName}.{oldExt}"):
        return

    if oldExt == "mp3":
        audioTag=eyed3.load(f"./audio/{fileName}.{oldExt}")
        title = audioTag.tag.title if title == "?" else title
        artist = audioTag.tag.artist if artist == "?" else artist
        album = audioTag.tag.album if album == "?" else album

    titleField = "title" if title != "?" else "genre"
    artistField = "artist" if artist != "?" else "genre"
    albumField = "album" if artist != "?" else "genre"

    if (title == "!"):
        title = ""

    if (artist == "!"):
        artist = ""

    if (album == "!"):
        album = ""

    global audio

    audio = AudioSegment.from_file(f"./audio/{fileName}.{oldExt}", oldExt )

    audio.export(f"./audio/{fileName}.mp3", format="mp3", tags={ titleField: title, artistField: artist, albumField: album})

    return f"./audio/{fileName}.mp3"