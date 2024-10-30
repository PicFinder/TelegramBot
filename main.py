import os
import logging

import telebot
import dotenv

import BackendAPI

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("PicFinderBot")

dotenv.load_dotenv()
bot = telebot.TeleBot(token=os.getenv("BOT_TOKEN"))


@bot.message_handler(content_types=['new_chat_members'])
def new_member_handler(message):
    chat_id = message.chat.id
    chat_name = message.chat.title
    logger.info(f"{chat_name} chat: bot added to chat")

    for new_member in message.new_chat_members:
        if new_member.id == bot.get_me().id:
            try:
                BackendAPI.create_chat(chat_id)
            except BackendAPI.BackendError as e:
                logger.error(str(e))
                return
            bot.send_message(chat_id,
                             "Hi! I can help you find photos in your chat\n\n"
                             "From now on, I will process the photos you send, sadly, I can't "
                             "process the photos in your chat history ¯\\_(ツ)_/¯ (yet...)\n\n"
                             "Use /find <description> to get a photo matching your description\n"
                             "To search for multiple photos use /find_<amount> <description>\n\n"
                             "Made by @zazamrykh @fedotovStanislav @azazuent")
            logger.info(f"{chat_name} chat: chat initialized")


@bot.message_handler(commands=["/start"])
def start_handler(message):
    chat_id = message.chat.id
    chat_name = message.chat.title
    logger.info(f"{chat_name} chat with user: bot added to chat")

    for new_member in message.new_chat_members:
        if new_member.id == bot.get_me().id:
            try:
                BackendAPI.create_chat(chat_id)
            except BackendAPI.BackendError as e:
                logger.error(str(e))
                return
            bot.send_message(chat_id,
                             "Hi! I can help you find photos in your chat\n\n"
                             "From now on, I will process the photos you send, sadly, I can't "
                             "process the photos in your chat history ¯\\_(ツ)_/¯ (yet...)\n\n"
                             "Use /find <description> to get a photo matching your description\n"
                             "To search for multiple photos use /find_<amount> <description>\n\n"
                             "Made by @zazamrykh @fedotovStanislav @azazuent")
            logger.info(f"{chat_name} chat with user: chat initialized")


@bot.message_handler(regexp=r"^\/find(_\d+)? ?[\s\S]*$")
def find_photo(message: telebot.types.Message):
    chat_id = message.chat.id
    chat_name = message.chat.title
    logger.info(f"{chat_name} chat: find request received")

    message_parts = message.text.split(" ", maxsplit=1)

    if len(message_parts) < 2:
        bot.reply_to(message, "Description required to find a photo")
        logger.info(f"{chat_name} chat: received /find with no description")
        return

    command, description = message_parts
    if "_" in command:
        if "@" in command:
            photo_amount = int(command.split("_", 1)[1].split("@", 1)[0])
        else:
            photo_amount = int(command.split("_", 1)[1])
    else:
        photo_amount = 1

    if not 1 <= photo_amount <= 10:
        bot.reply_to(message, "Photo amount should be in the 1-10 range")
        logger.info(f"{chat_name} chat: received /find with incorrect photo amount")
        return

    try:
        file_ids = BackendAPI.find_photo(description, photo_amount, chat_id)
    except BackendAPI.BackendError as e:
        logger.error(str(e))
        return

    if not file_ids:
        bot.reply_to(message, "No photos have been processed yet")
        logger.info(f"{chat_name} chat: no matching photos")
        return

    media_group = [telebot.types.InputMediaPhoto(file_id) for file_id in file_ids]
    bot.send_media_group(chat_id, media_group, reply_to_message_id=message.id)

    logger.info(f"{chat_name} chat: processed a request to find {photo_amount} photos "
                f"related to \"{description}\"")


@bot.message_handler(content_types=["photo"])
def process_photo(message: telebot.types.Message):
    chat_id = message.chat.id
    chat_name = message.chat.title
    logger.info(f"{chat_name} chat: caught a photo")

    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    photo = bot.download_file(file_info.file_path)
    try:
        BackendAPI.process_photo(photo, file_id, chat_id)
    except BackendAPI.BackendError as e:
        logger.error(f"{chat_name}: {str(e)}")
        return

    logger.info(f"{chat_name} chat: processed photo")


if __name__ == "__main__":
    logger.info("Starting PicFinder Telegram bot")
    bot.infinity_polling()
    logger.info("Shutting down PicFinder Telegram bot")
