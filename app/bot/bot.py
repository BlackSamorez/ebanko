from email.mime import application
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, MessageHandler, filters
from telegram import Update

from random import random

import logging
import requests

from time import sleep
from json import load, dump
from threading import Thread
from os.path import exists

from database import Handler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler("/persistent/bot/bot.log", "a")
fh.setFormatter(formatter)
logger.addHandler(fh)

TEMP = 1.5

if not exists("/persistent/perc.json"):
    logger.info("New perc")
    PERCENTAGES = {}
else:
    logger.info("Loading perc")
    with open("/persistent/perc.json", "r") as file:
        PERCENTAGES = dict(load(file))
    PERCENTAGES = {int(key): value for key, value in PERCENTAGES.items()}

DATABASE_HANDLER = Handler()


BACKEND_ADDRESS = "http://app:8080/predict"


async def toxify_private(update: Update, context: CallbackContext):
    try:
        reply = requests.post(BACKEND_ADDRESS, json={"text": update.message.text, "temp": TEMP}).json()["toxified"]
        DATABASE_HANDLER.insert(update.effective_chat.id, update.message.text, reply)
    except requests.exceptions.ConnectionError:
        logging.exception("ConnectionError")
        reply = "Я бы что-то ответил, но бэкенд умер нахуй"
        DATABASE_HANDLER.insert(update.effective_chat.id, update.message.text, None)
        pass

    await update.message.reply_text(text=reply)
    DATABASE_HANDLER.flush()
    

async def toxify_groups(update: Update, context: CallbackContext):
    if update.effective_chat.id not in PERCENTAGES.keys():
        logger.info(f"Adding chat {update.effective_chat.id}")
        PERCENTAGES[update.effective_chat.id] = 0.1
    perc = PERCENTAGES[update.effective_chat.id]

    logger.info("Entering group toxification")
    if random() < perc:
        try:
            reply = requests.post(BACKEND_ADDRESS, json={"text": update.message.text, "temp": TEMP}).json()["toxified"]
            DATABASE_HANDLER.insert(update.effective_chat.id, update.message.text, reply)
        except requests.exceptions.ConnectionError:
            logging.exception("ConnectionError")
            reply = "Я бы что-то ответил, но бэкенд умер нахуй"
            DATABASE_HANDLER.insert(update.effective_chat.id, update.message.text, None)
            pass
            
        await update.message.reply_text(text=reply)
        DATABASE_HANDLER.flush()
    

async def update_perc(update: Update, context: CallbackContext):
    global PERCENTAGES
    
    if update.effective_chat.id not in PERCENTAGES.keys():
        PERCENTAGES[update.effective_chat.id] = 0.1

    if len(context.args) > 0 and float(context.args[0]) >= 0 and float(context.args[0]) <= 1:
        PERCENTAGES[update.effective_chat.id] = float(context.args[0])
    await update.message.reply_text(text=f"Setting percentage {float(PERCENTAGES[update.effective_chat.id])}")


def main():
    logger.info("Bot restarted")
    app = ApplicationBuilder().token('').concurrent_updates(True).build()

    private_toxify_handler = MessageHandler(filters.TEXT & (~filters.COMMAND) & filters.ChatType.PRIVATE, toxify_private)
    app.add_handler(private_toxify_handler)
    groups_toxify_handler = MessageHandler(filters.TEXT & (~filters.COMMAND) & filters.ChatType.GROUPS, toxify_groups)
    app.add_handler(groups_toxify_handler)
    update_perc_handler = CommandHandler("perc", update_perc)
    app.add_handler(update_perc_handler)
    logger.info("Ready to poll")
    app.run_polling()
    logger.info("Polling")

def saver():
    logger.info("Starting saver")
    sleep(10)
    while True:
        logger.info("Saving")
        with open("perc", "w") as file:
            dump(PERCENTAGES, file)
        logger.info("Saved")
        sleep(10)

if __name__ == "__main__":
    saver_thread = Thread(target=saver)
    saver_thread.start()
    main()
