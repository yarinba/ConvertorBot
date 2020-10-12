import ast
import json
import traceback
from CoreFuncs.Settings import *
from urllib.request import urlopen

def simplify(call):
    try:
        return ast.literal_eval(call.data)
    except:
        return ['0', '11']

def btn(text=None, callback_data=None, url=None, Home=False, Dummy=False):
    if Home:
        return btn('חזרה לתפריט הראשי', ['Menu', '0'])
    if Dummy:
        return btn(text, ['Dummy_Button'])
    if callback_data:
        callb =  "['"
        for value in callback_data:
            callb += str(value)+"','"
        callb = callb[:-3] + "']"
        return types.InlineKeyboardButton(text=text, callback_data=callb)
    elif url:
        if type(url) == tuple: url = url[0]
        return types.InlineKeyboardButton(text=text, url='https://t.me/' + url)

class BotHandlers:
    @staticmethod
    @bot.message_handler(commands=['start'])
    def handle_command_start(message):
        chat_id = str(message.chat.id)
        try:
            bot.send_message(chat_id, CurrencyConverter.Header(), reply_markup=CurrencyConverter.Keyboard())
        except:
            traceback.print_exc()

    @staticmethod
    @bot.message_handler(commands=['update'])
    def handle_command_update(message):
        CurrencyConverter.update_Currencies()

    @staticmethod
    @bot.callback_query_handler(func=lambda call: True)
    def handle_all_button_clicks(call):
        chat_id = str(call.from_user.id)
        # ['Admin', 'Settings', 'update', 'Status', '0']
        try:
            # Menu inside menu
            if simplify(call)[0] == 'Dummy_Button':
                return
            class_name = simplify(call)[0]
            method = globals()[f'{class_name}']
            method(chat_id, simplify(call))
        except:
            traceback.print_exc()
            #print('chat id -', chat_id, 'in Menu -', simplify(call)[1])

class CurrencyConverter:
    def __init__(self, chat_id, data):
        self.chat_id = chat_id
        self.data = data
        self.method_name = data[1]
        method = getattr(self, self.method_name, lambda: 'Invalid')
        method()

    @staticmethod
    def Header():
        text = 'תפריט'

        return text

    @staticmethod
    def Keyboard():
        markup = types.InlineKeyboardMarkup()
        markup.add(btn('Update Rates', callback_data=['CurrencyConverter', 'update_Currencies']))
        markup.add(btn('Convert ILS', callback_data=['CurrencyConverter', 'get_currency']))
        return markup

    def update_Currencies(self):
        with urlopen("http://www.floatrates.com/daily/ils.json") as f:
            source = f.read()
        data = json.loads(source)
        # print(json.dumps(data, indent = 2))
        ils_rates = dict()

        for item in data:
            name = data[item]["code"]
            price = data[item]["inverseRate"]
            ils_rates[name] = price

        CR.dump(ils_rates)

    def get_currency(self):
        def kb():
            markup = types.ReplyKeyboardMarkup()
            my_currencies = CR.get().keys()
            curr_list = [types.KeyboardButton(x) for x in my_currencies]
            chunks = [curr_list[x:x + 3] for x in range(0, len(curr_list), 3)]
            for row in chunks:
                markup.add(*row)
            return markup

        text = f'Welcome, please choose currency that you\nwant to convert to from ILS:'
        msg = bot.send_message(self.chat_id, text, reply_markup=kb())
        bot.register_next_step_handler(msg, CurrencyConverter.get_amount)

    @staticmethod
    def get_amount(message):
        chat_id = str(message.chat.id)
        u_c = message.text
        if not u_c in CR.get().keys():
            error_text = f'please use valid currency'
            msg = bot.send_message(chat_id, error_text)
            bot.register_next_step_handler(msg, CurrencyConverter.get_amount)
            return
        UC.set(chat_id, u_c)
        text = f'please enter the amount of ILS\nyou would like to convert'
        msg = bot.send_message(chat_id, text)
        bot.register_next_step_handler(msg, CurrencyConverter.convert)

    @staticmethod
    def convert(message):
        chat_id = str(message.chat.id)
        try:
            c_amount = float(message.text)
        except ValueError:
            text = f'please use numbers only'
            msg = bot.send_message(chat_id, text)
            bot.register_next_step_handler(msg, CurrencyConverter.convert)

            return
        c_type = UC.get(chat_id)
        rate = CR.get(c_type)
        text = f'{c_amount} ILS are {(c_amount / rate):.2f} {c_type}'
        bot.send_message(chat_id, text)
        BotHandlers.handle_command_start(message)




bot.polling()