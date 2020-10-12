import functools
import json
import sqlite3
import logging
import traceback
from threading import Lock
from telebot import *
import os.path

class AtmoicResource:
    __slots__ = ['mutex']
    def __init__(self):
        self.mutex = Lock()

    def wrap(func):
        @functools.wraps(func)
        def decorate(self, *args, **kwargs):
            self.mutex.acquire(1)
            res = func(self, *args, **kwargs)
            self.mutex.release()
            if res is not None: return res

        return decorate

class Log(Exception):
    __slots__ = ['func_name']
    def __init__(self):
        self.func_name = traceback.extract_stack(None, 2)[0][2]
    def Pass(self,chat_id):
        logging.error(str(chat_id) + f":Pass exception occurred in " + self.func_name + f" -> {traceback.format_exc()}")
        #logging.info((chat_id + f":Pass exception occurred in " + self.func_name))
    def Warn(self,chat_id='Unknown', msg=' '):
        logging.warning(str(chat_id) + ": " + f"An Unexcepted error occurred in " + self.func_name + ". " + msg +"-> ",
                        exc_info=True)
    def Info(self, chat_id, txt):
        logging.info(chat_id + ": " + txt)

    def In(self,chat_id: object) -> object:
        logging.info(str(chat_id) + ": in " + self.func_name)

    def Choice(self, chat_id, txt):
        logging.info(chat_id + ": Action: " + txt)
#log = Log()


class Myjson(AtmoicResource):
    __slots__ = ['file']
    def __init__(self, file_path):
        super().__init__()
        self.file = file_path
        if not os.path.isfile(self.file):
            with open(file_path, 'w', encoding='utf8') as outfile:
                json.dump({}, outfile, indent=2)


    @AtmoicResource.wrap
    def get(self, *args):
        """
        get() -> all json dict
        get("key") -> get the value of given "key"
        get("keylv1", "keylv2") ->
        :param args:
        :return:
        """
        with open(self.file, encoding='utf8') as json_file:
            data = json.load(json_file)
        try:
            tmp = data
            for key in args:
                tmp = tmp[key]
        except KeyError:
            return None
        return tmp

    @AtmoicResource.wrap
    def oldget(self, key = False):
        with open(self.file, encoding = 'utf8') as json_file:
            data = json.load(json_file)
            if not key:
                return data
            elif key in data:
                return data[key]
            return None

    @AtmoicResource.wrap
    def set(self, *args):
        """
        :param args: dict path divided as arguments
                    for exmaple dict{"a": {"b":1}}
                    -> set("a", "b", 2) will set b value as 2 inside nested b dict
        """
        with open(self.file, encoding = 'utf8') as json_file:
            data = json.load(json_file)

        tmp = data
        for key in args[:-2]:
            tmp = tmp[key]
        tmp[args[-2]] = args[-1]

        with open(self.file, 'w', encoding = 'utf8') as outfile:
            json.dump(data, outfile, indent=2)

    @AtmoicResource.wrap
    def oldset(self, key, value):
        with open(self.file, encoding = 'utf8') as json_file:
            data = json.load(json_file)
            data[key] = value

        with open(self.file, 'w', encoding = 'utf8') as outfile:
            json.dump(data, outfile, indent=2)

    @AtmoicResource.wrap
    def add_to_list(self, key, value):

        with open(self.file, encoding = 'utf8') as json_file:
            data = json.load(json_file)
            if key not in data:
                data[key] = [value]
            else:
                data[key].append(value)

        # Save JSON file
        with open(self.file, 'w', encoding = 'utf8') as outfile:
            json.dump(data, outfile, indent=2)

    @AtmoicResource.wrap
    def remove_from_list(self, key, value):
        with open(self.file, encoding = 'utf8') as json_file:
            data = json.load(json_file)
        try:
            data[key].remove(value)
            # Save JSON file
            with open(self.file, 'w', encoding = 'utf8') as outfile:
                json.dump(data, outfile, indent=2)
        except:
            pass

    @AtmoicResource.wrap
    def delVal(self,key):
        with open(self.file, encoding = 'utf8') as json_file:
            data = json.load(json_file)
            data.pop(key, None)

        with open(self.file, 'w', encoding = 'utf8') as outfile:
            json.dump(data, outfile, indent=2)

    @AtmoicResource.wrap
    def dump(self, data):
        # Save JSON file
        with open(self.file, 'w', encoding = 'utf8') as outfile:
            json.dump(data, outfile, indent=2)

    @AtmoicResource.wrap
    def CompareMasterJson(self, slaveFile):
        master = self.get()
        slaveFile.dump(list(set(slaveFile.get()) - set(master)))

class DBgetset(AtmoicResource):
    __slots__ = ['c', 'connection']

    def __init__(self, db_name):
        super().__init__()
        self.connection = sqlite3.connect(db_name, check_same_thread=False)
        self.c = self.connection.cursor()

    def fix(self, values):
        newStr = ""
        for value in values:
            ask = (value != 'NULL')
            newStr += f"'{str(value)}'," if ask else 'NULL,'
        return newStr[:-1]

    @AtmoicResource.wrap
    def get(self, table, select='*', where='TRUE'):
        try:
            #SQL_Query = pd.read_sql_query(f"SELECT {select} FROM {table} WHERE {where}", self.connection)
            where_pharse = "WHERE " + where if where != 'TRUE' else ""
            self.c.execute(f"SELECT {select} FROM {table} {where_pharse}")
            try:
                count = self.c.fetchall()[0] if where != 'TRUE' else self.c.fetchall()
            except:
                count = self.c.fetchall()
            return count
        except IndexError:
            raise IndexError

    @AtmoicResource.wrap
    def work_get(self, username='TRUE'):
        try:
            #SQL_Query = pd.read_sql_query(f"SELECT {select} FROM {table} WHERE {where}", self.connection)
            where_pharse = "WHERE UserName=%s", username
            self.c.execute(f"SELECT ReviewCh FROM Users {where_pharse}")
            count = self.c.fetchall()[0] if username != 'TRUE' else self.c.fetchall()
            return count
        except IndexError:
            raise IndexError

    @AtmoicResource.wrap
    def insert(self, table, values):
        self.c.execute(f"INSERT INTO {table} VALUES ({values})")
        self.connection.commit()

    @AtmoicResource.wrap
    def insertPost(self, caption, media_id, file_type, user):
        try:
            self.connection.execute("INSERT INTO Posts VALUES (?,?,?,?,?)", (None, caption, media_id, file_type, user))
            self.connection.commit()
            return 1
        except sqlite3.OperationalError as e:
            print(e.args)
            return 0


    @AtmoicResource.wrap
    def insert_replace(self, table, values):
        try:
            self.c.execute(f"INSERT OR REPLACE INTO {table} VALUES ({self.fix(values)})")
            self.connection.commit()
        except sqlite3.OperationalError as e:
            print(e.args)

    @AtmoicResource.wrap
    def update(self, table, set_list, where):
        '''

        usage example:
        update("users", {"username": "til", "age": 5}, WHERE statement)

        '''
        set_string = ""
        for value in set_list:
            set_string += f"{value} = '{set_list[value]}', "
        set_string = set_string[:-2]
        where_pharse = 'WHERE '+where if where != 'TRUE' else ''
        pharse = f"UPDATE {table} SET {set_string} {where_pharse}"
        self.connection.execute(pharse)
        self.connection.commit()

    @AtmoicResource.wrap
    def delete(self, table, where):#BUG function isnt ready
        try:
            self.c.execute(f"DELETE FROM {table} WHERE {where}")
            self.connection.commit()
            return True
        except:
            return False

class Keyboard:
    __slots__ = ['Keyboards', 'Version']
    def __init__(self, file, ver):
        self.Keyboards = Myjson(file)
        self.Version = ver

    def btn(self, text=None, callback_data=None, url=None, Ver=True, Home=False, Dummy=False):
        if Home:
            return self.btn('חזרה לתפריט הראשי', ['Menu', '0'])
        if Dummy:
            return self.btn(text, ['Dummy_Button'])
        if callback_data:
            callback_data.insert(0, self.Version) if Ver else None
            callb = "['"
            for value in callback_data:
                callb += str(value) + "','"
            callb = callb[:-3] + "']"
            return types.InlineKeyboardButton(text=text, callback_data=callb)
        elif url:
            return types.InlineKeyboardButton(text=text, url='https://t.me/' + url)

    def kb_builder(self, Menu):
        menu_buttons = self.Keyboards.get(Menu)
        markup = types.InlineKeyboardMarkup()
        for button in menu_buttons:
            # Check if button is not a function
            if 'eval_link' in button:
                text = button['text']
                link = eval(button['eval_link'])()
                markup.add(self.btn(text, url=link))
                continue
            if 'func' not in button:
                # Check if button has a callback data
                if 'callback' in button:
                    markup.add(self.btn(button['text'], callback_data=[Menu] + button['callback']))
                else:  # Button is a link
                    markup.add(self.btn(button['text'], link=button['link']))
            else:  # Button is a function
                method = eval(button['func']['name']) if 'obj' not in button['func'] else \
                    getattr(eval(button['func']['obj']), button['func']['name'], lambda: 'Invalid')
                method()
                return
        return markup


