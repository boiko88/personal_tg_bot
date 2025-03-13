from telegram import Update, ReplyKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

import subprocess
import requests
import os
import speech_recognition as sr
from gtts import gTTS
from loguru import logger

from keys import OCR_TOKEN, BOT_TOKEN

TOKEN = BOT_TOKEN


async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [[
        '📸 Get text from image',
        '🎵 Extract audio from video',
        '🎤 Get text from audio',
        '🎵 Get audio from text'
    ]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text('What do you want to do?', reply_markup=reply_markup)


async def handle_choice(update: Update, context: CallbackContext) -> None:
    choice = update.message.text

    if choice == '📸 Get text from image':
        await update.message.reply_text('Send me an image!')
    elif choice == '🎵 Extract audio from video':
        await update.message.reply_text('Send me a video!')
    elif choice == '🎤 Get text from audio':
        await update.message.reply_text('Send me an audio file or a voice message!')
    elif choice == '🎵 Get audio from text':
        await update.message.reply_text('Send me some text or a .txt file!')
        context.user_data['awaiting_text_to_audio'] = True
    else:
        await update.message.reply_text('Please choose a valid option.')


async def handle_video(update: Update, context: CallbackContext) -> None:
    video = update.message.video or update.message.document
    if not video:
        return await update.message.reply_text('Please send a valid video file.')

    file = await context.bot.get_file(video.file_id)
    video_path = 'input_video.mp4'  
    audio_path = 'extracted_audio.mp3'

    await file.download_to_drive(video_path)
    subprocess.run(['ffmpeg', '-i', video_path, '-q:a', '0', '-map', 'a', audio_path], check=True)

    await update.message.reply_audio(audio=open(audio_path, 'rb'))

    os.remove(video_path)
    os.remove(audio_path)


async def handle_photo(update: Update, context: CallbackContext) -> None:
    photo = update.message.photo[-1]  
    file = await context.bot.get_file(photo.file_id)
    image_url = file.file_path  

    ocr_token = OCR_TOKEN
    image_content = requests.get(image_url).content  

    response = requests.post(
        'https://api.ocr.space/parse/image',
        files={'file': ('image.jpg', image_content)},  
        data={'apikey': ocr_token, 'language': 'eng'}
    )

    try:
        result = response.json()
        if 'ParsedResults' in result and result['ParsedResults']:
            text = result['ParsedResults'][0]['ParsedText']
            await update.message.reply_text(f'Extracted Text:\n{text}')
        else:
            await update.message.reply_text('No text found or an error occurred.')
    except Exception as e:
        await update.message.reply_text('Error processing image.')
        print('Error:', e)


async def handle_audio(update: Update, context: CallbackContext) -> None:
    audio = update.message.voice or update.message.audio
    if not audio:
        return await update.message.reply_text('Please send a valid audio file.')

    file = await context.bot.get_file(audio.file_id)
    audio_path = 'input_audio.ogg'
    converted_audio_path = 'converted_audio.wav'

    await file.download_to_drive(audio_path)
    subprocess.run(['ffmpeg', '-i', audio_path, '-ar', '16000', '-ac', '1', converted_audio_path], check=True)

    recognizer = sr.Recognizer()
    with sr.AudioFile(converted_audio_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            await update.message.reply_text(f'Transcribed Text:\n{text}')
        except sr.UnknownValueError:
            await update.message.reply_text('Sorry, I could not understand the audio.')
        except sr.RequestError:
            await update.message.reply_text('Error with the speech recognition service.')

    os.remove(audio_path)
    os.remove(converted_audio_path)


async def handle_document(update: Update, context: CallbackContext) -> None:
    file = await context.bot.get_file(update.message.document.file_id)

    if update.message.document.mime_type == 'text/plain':
        file_path = 'input_text.txt'
        await file.download_to_drive(file_path)

        with open(file_path, 'r') as f:
            text = f.read()

        tts = gTTS(text)
        audio_path = 'output.mp3'
        tts.save(audio_path)

        await update.message.reply_audio(audio=open(audio_path, 'rb'))
        os.remove(file_path)
        os.remove(audio_path)
    else:
        await update.message.reply_text('I only accept .txt files for now.')


app = Application.builder().token(TOKEN).build()

# Handlers
app.add_handler(CommandHandler('start', start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choice))
app.add_handler(MessageHandler(filters.VIDEO, handle_video))
app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_audio))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_document))
app.add_handler(MessageHandler(filters.Document.ALL, handle_document))


if __name__ == '__main__':
    logger.debug('The Bot is launched')
    app.run_polling()
