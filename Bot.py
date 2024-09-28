import os
import logging

import telebot
import dotenv

import BackendAPI

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("PicFinderBot")

dotenv.load_dotenv()
bot = telebot.TeleBot(token=os.getenv("token"))


@bot.message_handler(regexp=r"find(_([1-9]|10))?")
def find_photo(message: telebot.types.Message):
    chat_id = message.chat.id
    chat_name = message.chat.title
    message_parts = message.text.split(" ", maxsplit=1)

    if len(message_parts) < 2:
        bot.reply_to(message, "Description required to find a photo")
        logger.info(f"{chat_name}: received /find with no description")
        return

    command, description = message_parts
    if "_" in command:
        photo_amount = int(command.split("_")[1])
    else:
        photo_amount = 1

    try:
        file_ids = BackendAPI.find_photo(description, photo_amount, chat_id)
    except BackendAPI.BackendError as e:
        logger.error(str(e))
        return

    media_group = [telebot.types.InputMediaPhoto(file_id) for file_id in file_ids]
    bot.send_media_group(chat_id, media_group, reply_to_message_id=message.id)

    logger.info(f"{chat_name}: Processed request to find {photo_amount} photos")


@bot.message_handler(content_types=["photo"])
def process_photos(message: telebot.types.Message):
    chat_id = message.chat.id
    chat_name = message.chat.title

    for file in message.photo:
        file_info = bot.get_file(file.file_id)
        photo = bot.download_file(file_info.file_path)
        try:
            BackendAPI.process_photo(photo, file.file_id, chat_id)
        except BackendAPI.BackendError as e:
            logger.error(f"{chat_name}: {str(e)}")
            continue

    logger.info(f"{chat_name}: Processed {len(message.photo)} photos")


if __name__ == "__main__":
    logger.info("Starting PicFinder Telegram bot")
    bot.infinity_polling()
    logger.info("Shutting down PicFinder Telegram bot")
