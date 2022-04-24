from tgbot.string_evolver import evolution as ev
from tgbot.bot.bot import telegram_bot

def run():
    with open('token', 'r') as file:
        token = file.read().rstrip()

    bot = telegram_bot(token)
    bot.start()