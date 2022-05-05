from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async
from telegram import Update

from random import random

import logging
import requests

import dbm

from time import sleep
from json import load, dump
from threading import Thread
from os.path import exists

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

pid = "/bot/bot.pid"
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler("/bot/bot.log", "a")
fh.setFormatter(formatter)
logger.addHandler(fh)

TEMP = 1.5

if not exists("perc"):
	logger.info("New perc")
	PERCENTAGES = {}
else:
	logger.info("Loading perc")
	with open("perc", "r") as file:
		PERCENTAGES = dict(load(file))
	PERCENTAGES = {int(key): value for key, value in PERCENTAGES.items()}
	logger.info(f"perc: {PERCENTAGES}")

BACKEND_ADDRESS = "http://app:8080/predict"


@run_async
def toxify_private(update: Update, context: CallbackContext):
    logger.info("Entering private toxification")
    try:
    	reply = requests.post(BACKEND_ADDRESS, json={"text": update.message.text, "temp": TEMP}).json()["toxified"]
    except requests.exceptions.ConnectionError:
    	logging.exception("ConnectionError")
    	reply = "Я бы что-то ответил, но бэкенд умер нахуй"
    	pass

    context.bot.send_message(chat_id=update.effective_chat.id, text=reply)
    logger.info("Exiting private toxification")

@run_async
def toxify_groups(update: Update, context: CallbackContext):
	if update.effective_chat.id not in PERCENTAGES.keys():
		logger.info(f"Adding chat {update.effective_chat.id}")
		PERCENTAGES[update.effective_chat.id] = 0.1
	perc = PERCENTAGES[update.effective_chat.id]

	logger.info("Entering group toxification")
	if random() < perc or update.message.reply_to_message.from_user(SELF_ID):
		logger.info("Applying group toxification")
		try:
			reply = requests.post(BACKEND_ADDRESS, json={"text": update.message.text, "temp": TEMP}).json()["toxified"]
		except requests.exceptions.ConnectionError:
			logging.exception("ConnectionError")
			reply = "Я бы что-то ответил, но бэкенд умер нахуй"
			pass
			
		context.bot.send_message(chat_id=update.effective_chat.id, text=reply, reply_to_message_id=update.message.message_id)
	logger.info("Exiting group toxification")
	

@run_async
def update_perc(update: Update, context: CallbackContext):
	global PERCENTAGES

	logger.info(f"Updating chat {update.effective_chat.id}")
	
	if update.effective_chat.id not in PERCENTAGES.keys():
		PERCENTAGES[update.effective_chat.id] = 0.1

	if len(context.args) > 0 and float(context.args[0]) >= 0 and float(context.args[0]) <= 1:
		PERCENTAGES[update.effective_chat.id] = float(context.args[0])
	context.bot.send_message(chat_id=update.effective_chat.id, text=f"Setting percentage {float(PERCENTAGES[update.effective_chat.id])}")


def main():
	logger.info("Bot restarted")
	updater = Updater(token='', use_context=True, workers=4)
	SELF_ID = updater.bot.bot.id
	dispatcher = updater.dispatcher

	private_toxify_handler = MessageHandler(Filters.text & (~Filters.command) & Filters.chat_type.private, toxify_private, run_async=True)
	dispatcher.add_handler(private_toxify_handler)
	groups_toxify_handler = MessageHandler(Filters.text & (~Filters.command) & Filters.chat_type.groups, toxify_groups, run_async=True)
	dispatcher.add_handler(groups_toxify_handler)
	update_perc_handler = CommandHandler("perc", update_perc, run_async=True)
	dispatcher.add_handler(update_perc_handler)
	logger.info("Ready to poll")
	updater.start_polling()
	logger.info("Polling")

def saver():
	logger.info("Starting saver")
	sleep(10)
	while True:
		logger.info("Saving")
		with open("perc", "w") as file:
			dump(PERCENTAGES, file)
		logger.info("Saved")
		sleep(600)

if __name__ == "__main__":
	saver_thread = Thread(target=saver)
	saver_thread.start()
	main()
