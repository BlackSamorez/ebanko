from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters
from telegram import Update

import logging
import requests

TEMP = 1.5

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

def toxify(update: Update, context: CallbackContext):
    reply = "Something went wrong!"
    try:
    	reply = requests.post("http://localhost:8080/predict", json={"text": update.message.text, "temp": TEMP}).json()["toxified"]
    except RuntimeError as er:
    	logging.exception("No response")
    	pass

    context.bot.send_message(chat_id=update.effective_chat.id, text=reply)

def update_temp(update: Update, context: CallbackContext):
	global TEMP
	if len(context.args) > 0 and float(context.args[0]) > 0:
		TEMP = float(context.args[0])
	context.bot.send_message(chat_id=update.effective_chat.id, text=f"Set temperature {TEMP}")

if __name__ == "__main__":
	updater = Updater(token='', use_context=True)
	dispatcher = updater.dispatcher

	toxify_handler = MessageHandler(Filters.text & (~Filters.command), toxify)
	dispatcher.add_handler(toxify_handler)
	update_temp_handler = CommandHandler("temp", update_temp)
	dispatcher.add_handler(update_temp_handler)
	updater.start_polling()
