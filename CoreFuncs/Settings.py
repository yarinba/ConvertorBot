import telebot
from telebot import *
from CoreFuncs.resources import Myjson

CR = Myjson('res/Currency.json') # RAM setting
JS = Myjson('res/settings.json') # Settings
UC = Myjson('res/UserChoice.json') #User currency choice

bot = telebot.TeleBot(JS.get('Token')[0])
print(f"Delete Webhook - {bot.delete_webhook()}")
