from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup
import logging
import json
import os

from utils import *

from searcher.backend import Backend
backend = Backend(index_file='full_index', meta_data_file='titles_and_types.csv.tsv')

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

actions = {
    'NEXT':   '1',
    'PREV':   '2',
    'SEARCH': '3'
}

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
        bot.send_message(query.message.chat_id, '--------------------------')
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

    if iterator < len(to_iterate):
        doc = to_iterate[iterator]

        update.message.reply_text('Title: "{}"'.format(doc['title']))
        update.message.reply_text('Type: "{}"'.format(doc['type']))

        categ = category(doc)
        update.message.reply_text('Category: {}'.format(categ))
        update.message.reply_text('Document {}'.format(iterator+1))

        keywords = doc['keywords'][:10]
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

    # to_iterate = os.listdir('jsons')
    glob_stats, to_iterate = backend.process_query(query)
    iterator = 0

    update.message.reply_text('Total found: {}'.format(glob_stats['docs_found']))

    if glob_stats['sentiment'] > 0:
        update.message.reply_text('Average sentiment: positive')
    else:
        update.message.reply_text('Average sentiment: negative')
    update.message.reply_text('All locations: {}'.format(glob_stats['locations']))
    update.message.reply_text('All categories: {}'.format(glob_stats['categories']))

    keywords = glob_stats['keywords'][:10]
    wcloud_path = "wordClouds/" + chat_id + '.png'
    make_wordcloud(keywords, wcloud_path)

    with open(wcloud_path, 'rb') as f:
        update.message.reply_photo(photo=f)

    # send_doc(update)

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Choose something', reply_markup=reply_markup)


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
