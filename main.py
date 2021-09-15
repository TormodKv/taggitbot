from telegram import Update, update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, dispatcher
import logging
import tagger
import os
import json

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def help_handler(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Upload a file or a recording to start!\n\nUse /cancel to cancel the operation.\n\nWhen tagging use "!" to clear the value\n and "?" to keep the existing values')


def cancel_handler(update: Update, context: CallbackContext) -> None:
    json_clear_user(update.effective_user.id)
    update.message.reply_text("Cancelled operation!")


def cleanup_handler(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != 52507774:
        update.message.reply_text(f'You are unauthorized')
        return

    cleanup_audio(1)
    cleanup_users()
    update.message.reply_text(f'Audio cleaned up!')


def cleanup_audio(userId):

    userId = str(userId)

    if (userId == '1'):
        for filename in os.listdir(f"{os.getcwd()}\\audio\\"):
            os.remove(f"{os.getcwd()}\\audio\\{filename}")
    else:
        f = open('./users.json')
        data = json.load(f)
        f.close()

        oldExt = data[userId]["oldExt"]

        os.remove(f'./audio/{data[userId]["fileName"]}.{oldExt}')
        if oldExt != "mp3":
            os.remove(f'./audio/{data[userId]["fileName"]}.mp3')

        return

def cleanup_users():
    filename = "./users.json"
    data = {}
    os.remove(filename)
    with open(filename, 'w') as f:
        json.dump(data, f)


def voice_handler(update: Update, context: CallbackContext):
    general_audio_handler(update, context, update.message.voice.file_id, "_.ogg")


def audio_handler(update: Update, context: CallbackContext):
    general_audio_handler(update, context, update.message.audio.file_id, update.message.audio.file_name)


def video_handler(update: Update, context: CallbackContext):
    general_audio_handler(update, context, update.message.video.file_id, update.message.video.file_name)


def document_handler(update: Update, context: CallbackContext):
    general_audio_handler(update, context, update.message.document.file_id, update.message.document.file_name)


def general_audio_handler(update: Update, context: CallbackContext, fileId, oldExt):
    json_add(update.effective_user.id, "fileId" , fileId)

    oldExt = oldExt.split(".")

    oldFileName = ""
    for i in range(len(oldExt)-1):
        oldFileName += oldExt[i]

    oldExt = oldExt[len(oldExt) - 1]

    json_add(update.effective_user.id, "oldExt" , oldExt)
    json_add(update.effective_user.id, "oldFileName" , oldFileName)
    text_handler(update, context)


def text_handler(update: Update, context: CallbackContext):

    mes = update.message.text or ""

    f = open('./users.json')
    data = json.load(f)
    f.close()
    uid = str(update.effective_user.id)

    # sent a message without a file
    if uid not in data:
        update.message.reply_text("Upload a file first")
        return

    if mes == "":
        update.message.reply_text("Filename:")
        return

    if 'fileName' not in data[uid]:
        if mes == "!":
            mes = "_"

        if mes == "?":
            json_add(uid, "fileName", data[uid]["oldFileName"])
        else:
            json_add(uid, "fileName", mes)
        update.message.reply_text("Artist:")
        return

    if 'artist' not in data[uid]:
        json_add(uid, "artist", mes)
        update.message.reply_text("Title:")
        return

    if 'title' not in data[uid]:
        json_add(uid, "title", mes)
        update.message.reply_text("Album:")
        return

    if 'album' not in data[uid]:
        json_add(uid, "album", mes)

    fileId = data[uid]['fileId']
    oldExt = data[uid]['oldExt']
    fileName = data[uid]['fileName']
    artist = data[uid]['artist']
    title = data[uid]['title']
    album = mes
    
    try:
        start(update, context, fileId, oldExt, fileName, artist, title, album)
    except:
        update.message.reply_text("Something went wrong 😢")
    finally:
        cleanup_audio(update.effective_user.id)
        json_clear_user(update.effective_user.id)
        

def start(update: Update, context: CallbackContext, fileId, oldExt, fileName, artist, title, album):

    file = context.bot.getFile(fileId)

    file.download(f"./audio/{fileName}.{oldExt}")
    newFullPath = tagger.tag(fileName, oldExt, title, artist, album)
    if len(newFullPath) > 0:
        update.message.reply_audio(audio=open(newFullPath, 'rb'))


def json_add(userId, fieldKey, fieldValue):

    userId = str(userId)

    filename = './users.json'
    with open(filename, 'r') as f:
        data = json.load(f)
        if userId not in data:
            data[userId] = {}
        data[userId][fieldKey] = str(fieldValue)

    os.remove(filename)
    with open(filename, 'w') as f:
        json.dump(data, f)


def json_clear_user(userId):

    userId = str(userId)

    filename = './users.json'
    with open(filename, 'r') as f:
        data = json.load(f)
        if userId not in data:
            return
        del data[userId]

    os.remove(filename)
    with open(filename, 'w') as f:
        json.dump(data, f)


updater = Updater('YOUR_KEY_HERE')
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('help', help_handler))
dispatcher.add_handler(CommandHandler('start', help_handler))
dispatcher.add_handler(CommandHandler('cleanup', cleanup_handler))
dispatcher.add_handler(CommandHandler('cancel', cancel_handler))
dispatcher.add_handler(MessageHandler(Filters.voice, voice_handler))
dispatcher.add_handler(MessageHandler(Filters.audio, audio_handler))
dispatcher.add_handler(MessageHandler(Filters.video, video_handler))
dispatcher.add_handler(MessageHandler(Filters.document, document_handler))
dispatcher.add_handler(MessageHandler(Filters.all, text_handler))

updater.start_polling()
updater.idle()