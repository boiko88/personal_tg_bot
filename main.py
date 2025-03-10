from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

import subprocess
import requests
import os

from keys import OCR_TOKEN, BOT_TOKEN

TOKEN = BOT_TOKEN


async def start(update: Update, context: CallbackContext):
    keyboard = [["📸 Get text from image", "🎵 Extract audio from video"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text("What do you want to do?", reply_markup=reply_markup)


async def handle_choice(update: Update, context: CallbackContext):
    choice = update.message.text

    if choice == "📸 Get text from image":
        await update.message.reply_text("Send me an image!")
    elif choice == "🎵 Extract audio from video":
        await update.message.reply_text("Send me a video!")
    else:
        await update.message.reply_text("Please choose a valid option.")


async def handle_video(update: Update, context: CallbackContext):
    video = update.message.video or update.message.document
    if not video:
        return await update.message.reply_text("Please send a valid video file.")

    file = await context.bot.get_file(video.file_id)
    video_path = f"input_video.mp4"  # Always save as MP4 for FFmpeg compatibility
    audio_path = "extracted_audio.mp3"

    await file.download_to_drive(video_path)
    subprocess.run(["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path], check=True)

    await update.message.reply_audio(audio=open(audio_path, "rb"))

    os.remove(video_path)
    os.remove(audio_path)


async def handle_photo(update: Update, context):
    photo = update.message.photo[-1]  # Get the highest resolution photo
    file = await context.bot.get_file(photo.file_id)
    image_url = file.file_path  # Get direct image URL

    # Use an OCR API here (example with OCR.space)
    ocr_token = OCR_TOKEN
    image_content = requests.get(image_url).content  # Get the image data

    response = requests.post(
        "https://api.ocr.space/parse/image",
        files={"file": ("image.jpg", image_content)},  # Fix file format
        data={"apikey": ocr_token, "language": "eng"}
    )

    # Print full response for debugging
    print("OCR API Response:", response.text)

    try:
        result = response.json()
        if "ParsedResults" in result and result["ParsedResults"]:
            text = result["ParsedResults"][0]["ParsedText"]
            await update.message.reply_text(f"Extracted Text:\n{text}")
        else:
            await update.message.reply_text("No text found or an error occurred.")
    except Exception as e:
        await update.message.reply_text("Error processing image.")
        print("Error:", e)


app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choice))
app.add_handler(MessageHandler(filters.VIDEO, handle_video))

if __name__ == '__main__':
    app.run_polling()
