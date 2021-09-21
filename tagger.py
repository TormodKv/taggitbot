from os import path
from pydub import AudioSegment
import eyed3


def tag(fileName : str, oldExt, title, artist, album):

    if not path.exists(f"./audio/{fileName}.{oldExt}"):
        return

    if not title.__contains__("www.activechristianity.org") or not title.__contains__("©SSSF"):
            title = f"{title} - www.activechristianity.org ©SSSF"

    if oldExt == "mp3":
        return handle_mp3(fileName, oldExt, artist, album, title)

    titleField = "title" if title != "? - www.activechristianity.org ©SSSF" else "genre"
    artistField = "artist" if artist != "?" else "genre"
    albumField = "album" if artist != "?" else "genre"

    if (title == "! - www.activechristianity.org ©SSSF"):
        title = ""

    if (artist == "!"):
        artist = ""

    if (album == "!"):
        album = ""

    global audio

    audio = AudioSegment.from_file(f"./audio/{fileName}.{oldExt}", oldExt )

    audio.export(f"./audio/{fileName}.mp3", format="mp3", tags={ titleField: title, artistField: artist, albumField: album, 'comments': "©SSSF - www.activechristianity.org", 'comment': "©SSSF - www.activechristianity.org", 'copyright': "Copyright © Stiftelsen Skjulte Skatters Forlag", 'publisher': 'Brunstad Christian Church'})

    return f"./audio/{fileName}.mp3"

# Only for mp3's
def handle_mp3(fileName, oldExt, artist, album, title):
    audiofile=eyed3.load(f"./audio/{fileName}.{oldExt}")

    title: str = audiofile.tag.title if title == "? - www.activechristianity.org ©SSSF" else title

    if title == "! - www.activechristianity.org ©SSSF":
        title = ""

    audiofile.tag.title = title

    if artist != "?":
        audiofile.tag.artist = artist if artist != "!" else ""

    if album != "?":
        audiofile.tag.album = album if album != "!" else ""

    audiofile.tag.copyright = "Copyright © Stiftelsen Skjulte Skatters Forlag"
    audiofile.tag.publisher = "Brunstad Christian Church"
    audiofile.tag.comment = "©SSSF - www.activechristianity.org"

    audiofile.tag.save()

    return f"./audio/{fileName}.mp3"

