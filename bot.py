from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup
import logging
import json
import os

from utils import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

actions = {
    'NEXT':   '1',
    'PREV':   '2',
    'SEARCH': '3'
}

# to_iterate = ['a', 'b', 'c', 'd']
iterator = 0
is_searching = False
to_iterate = None

# ------------------ #
#  Here goes bot's   #
#  Implementation    #
# ------------------ #


def get_token():
    path = 'token_sgs.json'
    with open(path, 'r') as jsn:
        data = json.load(jsn)
    return data['token']

keyboard = [[InlineKeyboardButton("Previous", callback_data=actions['PREV']),
             InlineKeyboardButton("Search by keyword",  callback_data=actions['SEARCH']),
             InlineKeyboardButton("Next", callback_data=actions['NEXT'])]]


def start(bot, update):
    update.message.reply_text('Start working...')
    update.message.reply_text('Please, enter the query:')

    # reply_markup = InlineKeyboardMarkup(keyboard)
    # update.message.reply_text('Please choose:', reply_markup=reply_markup)


def button(bot, update):
    global iterator
    global is_searching

    query = update.callback_query

    # NEXT case
    if query.data == actions['NEXT']:
        bot.edit_message_text(text="Ok, next",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        if iterator+1 < len(to_iterate):
            iterator += 1
            # bot.send_message(query.message.chat_id, to_iterate[iterator])
            send_doc(query)
        else:
            bot.send_message(query.message.chat_id, 'The End. Now send me another keyword')
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text('Choose something', reply_markup=reply_markup)

    # SEARCH case
    elif query.data == actions['SEARCH']:
        bot.edit_message_text(text="Ok, send me a keyword",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        is_searching = True

    # PREV case
    elif query.data == actions['PREV']:
        bot.edit_message_text(text="Ok, prev",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        if iterator > 0:
            iterator -= 1
            # bot.send_message(query.message.chat_id, to_iterate[iterator])
            send_doc(query)
        else:
            bot.send_message(query.message.chat_id, 'Move Next please')

        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text('Choose something', reply_markup=reply_markup)


def send_doc(update):
    chat_id = str(update.message.chat_id)

    if iterator+1 < len(to_iterate):
        doc = to_iterate[iterator]

        update.message.reply_text('Document {}/{}'.format(iterator+1, len(to_iterate)))
        update.message.reply_text(doc)

        keywords = get_keywords(doc, 10)
        keywords = list(map(lambda x: (x['text'], x['relevance']), keywords))

        wcloud_path = "wordClouds/" + chat_id + '.png'
        make_wordcloud(keywords, wcloud_path)

        with open(wcloud_path, 'rb') as f:
            update.message.reply_photo(photo=f)
    else:
        update.message.reply_text('The End.')


def rules_fun(bot, update):
    global to_iterate
    global iterator

    query = update.message.text
    chat_id = str(update.message.chat_id)

    to_iterate = os.listdir('jsons')
    iterator = 0

    update.message.reply_text('Total found: {}'.format(len(to_iterate)))
    send_doc(update)

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Choose something', reply_markup=reply_markup)

    # filename = '0a0d2676-2fbd-4265-9100-032489b44cc1.json'
    #
    # update.message.reply_text(filename)
    #
    # keywords = get_keywords(filename, 10)
    # keywords = list(map(lambda x: (x['text'], x['relevance']), keywords))
    #
    # wcloud_path = "wordClouds/" + chat_id + '.png'
    # make_wordcloud(keywords, wcloud_path)
    #
    # with open(wcloud_path, 'rb') as f:
    #     update.message.reply_photo(photo=f)

    # TODO: PASS Oleg function here
    #
    # 1. Get list of ranked documents
    #
    # index = DocumentsIndex()
    # index.load_index_from_file("checkpoint23000.dms")
    # index.fill_doc_len()
    # engine = Engine(index)
    #
    # update.message.reply_text(engine.process_query([query]))
    #
    #
    # 2. Make WordCloud for every returned document
    #
    # wcloud_path = "wordClouds/" + update.message.chatid
    # update.message.reply_photo(photoid)
    #
    #
    # 3. Iterate over returned image
    #


def help_function(bot, update):
    update.message.reply_text('Help!')


def error(bot, update, error_arg):
    logger.warning('Update "%s" caused error "%s"' % (update, error_arg))


def main():
    updater = Updater(get_token())
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_function))
    dp.add_error_handler(error)

    # on non-command messages
    dp.add_handler(MessageHandler(Filters.text, rules_fun))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    print("-> Hi!")
    main()
