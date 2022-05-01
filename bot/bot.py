from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async
from telegram import Update

import logging
import requests

TEMP = 1.5

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

@run_async
def toxify_private(update: Update, context: CallbackContext):
    logger.info("Entering private toxification")
    reply = "Something went wrong!"
    try:
    	reply = requests.post("http://localhost:8080/predict", json={"text": update.message.text, "temp": TEMP}).json()["toxified"]
    except ConnectionError as er:
    	logging.exception("No response")
    	pass

    context.bot.send_message(chat_id=update.effective_chat.id, text=reply)

@run_async
def toxify_group(update: Update, context: CallbackContext):
    logger.info("Entering group toxification")

def update_temp(update: Update, context: CallbackContext):
	global TEMP
	if len(context.args) > 0 and float(context.args[0]) > 0:
		TEMP = float(context.args[0])
	context.bot.send_message(chat_id=update.effective_chat.id, text=f"Set temperature {TEMP}")

def main():
	logger.info("Bot restarted")
	updater = Updater(token='', use_context=True)
	dispatcher = updater.dispatcher

	private_toxify_handler = MessageHandler(Filters.text & (~Filters.command), toxify_private)
	dispatcher.add_handler(private_toxify_handler)
	update_temp_handler = CommandHandler("temp", update_temp)
 # 	 dispatcher.add_handler(update_temp_handler)
	logger.info("Ready to poll")
	updater.start_polling()
	logger.info("Polling")

from daemonize import Daemonize

pid = "/home/blacksamorez/ebanko/bot/bot.pid"
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler("/home/blacksamorez/ebanko/bot/bot.log", "a")
fh.setFormatter(formatter)
logger.addHandler(fh)
keep_fds = [fh.stream.fileno()]

daemon = Daemonize(app="ebanko_bot", pid=pid, action=main, keep_fds=keep_fds)
daemon.start()
