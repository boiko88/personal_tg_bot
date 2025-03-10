from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import requests

from keys import OCR_TOKEN, BOT_TOKEN

TOKEN = BOT_TOKEN


async def start(update: Update, context):
    await update.message.reply_text("Send me an image, and I'll extract the text!")


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

if __name__ == '__main__':
    app.run_polling()
