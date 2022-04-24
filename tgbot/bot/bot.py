from enum import Enum
from tgbot.string_evolver.evolution import evolve
from tgbot.string_evolver import evolution
import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler
)

class States(Enum):
    CHOOSING, TYPING_REPLY = range(2)


class telegram_bot:
    def __init__(self, token):
        self.updater = Updater(token)
        self.__add_handlers__()

        self.default_conf = {
            'children_num': 30,
            'survivals_num': 30
        }

        self.options_match = {
            'Set number of childern': 'children_num',
            'Set number of survivals': 'survivals_num'
        }

        self.keyboards = {
            'root' : {
                'keyboard': [
                    ['Hello world!', 'Set number of childern', 'Set number of survivals'],
                    ['Show current configuration']
                ]
            }
        }

    def start(self):
        self.updater.start_polling()
        self.updater.idle()


    def enable_logging(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

        dp = self.updater.dispatcher
        dp.add_error_handler(self.__error__)
        self.logger = logging.getLogger(__name__)

    def __add_handlers__(self):
        dp = self.updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.__start__)],
            states={
                States.CHOOSING: [
                    MessageHandler(
                        Filters.regex('^(Set number of childern|Set number of survivals)$'),
                        self.__choice__
                    ),
                    MessageHandler(
                        Filters.regex('^(Show current configuration)$'),
                        self.__show_config__
                    ),
                    MessageHandler(
                        Filters.text,
                        self.__evolve__
                    ),
                ],
                States.TYPING_REPLY: [
                    MessageHandler(
                        Filters.text & ~(Filters.command),
                        self.__received_information__,
                    )
                ]  
            },
            fallbacks=[CommandHandler('cancel', self.__cancel__)],
        )

        dp.add_handler(conv_handler)

    def __cancel__(self, update, context):
        update.message.reply_text(
            'Bye!', reply_markup=ReplyKeyboardRemove()
        )

        return ConversationHandler.END

    def __start__(self, update, context):
        context.user_data.update(self.default_conf)

        update.message.reply_text(
            'Hi! Configure the evolution or just pass the desired text!',
            reply_markup=ReplyKeyboardMarkup(
                self.keyboards['root']['keyboard'], one_time_keyboard=True
            ),
        )

        return States.CHOOSING

    def __show_config__(self, update, context):
        config = (
            f'Number of children: {context.user_data["children_num"]}\n'
            f'Number of survivals: {context.user_data["survivals_num"]}'
        )

        update.message.reply_text(
            config,
            reply_markup=ReplyKeyboardMarkup(
                self.keyboards['root']['keyboard'], one_time_keyboard=True
            ),
        )

        return States.CHOOSING

    def __choice__(self, update, context):
        text = update.message.text
        context.user_data['choice'] = self.options_match[text]
        update.message.reply_text(f'Enter the number!')

        return States.TYPING_REPLY

    def __received_information__(self, update, context):
        user_data = context.user_data
        text = update.message.text
        category = user_data['choice']
        user_data[category] = text
        del user_data['choice']

        update.message.reply_text(
            "Config updated!",
            reply_markup=ReplyKeyboardMarkup(
                self.keyboards['root']['keyboard'], one_time_keyboard=True
            ),
        )

        return States.CHOOSING

    def __evolve__(self, update, context):
        user_data = context.user_data
        num = evolve(update.message.text.lower(), int(user_data['children_num']), int(user_data['survivals_num']))
        update.message.reply_text(f'It took {num} iterations to generate "{update.message.text}"')

        return States.CHOOSING

    def __error__(self, update, context):
        self.logger.warning('Update "%s" caused error "%s"', update, context.error)