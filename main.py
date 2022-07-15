import os
from pdb import lasti2lineno
import re
import json
import sqlite3
import logging
import requests

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from aiogram.utils import executor
from aiogram import Bot, types, filters
from aiogram.dispatcher import Dispatcher

database_name = 'userdata.db'

file_exists = os.path.exists(database_name)
conn = sqlite3.connect('userdata.db')
cur = conn.cursor()
cur.row_factory = lambda cursor, row: row[0]
load_dotenv('.env')
logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.environ.get('BOT_TOKEN'))
dp = Dispatcher(bot)
ACR_BEARER = os.environ.get('ACR_BEARER')

if file_exists == False:
    cur.execute("""CREATE TABLE IF NOT EXISTS admins(
    userid INT unique);
    """)
    conn.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS chats(
    chatid INT unique);
    """)
    conn.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS data(
    lastupc INT unique,
    stop INT);
    """)
    conn.commit()

    values_admins = 1999113390
    values_chats = -1001782706447
    values_data_lastupc = 3616849316225
    values_data_stop = 1
    cur.execute(f"INSERT OR IGNORE INTO admins VALUES({values_admins});")
    cur.execute(f"INSERT OR IGNORE INTO chats VALUES({values_chats});")
    cur.execute(f"INSERT OR IGNORE INTO data VALUES({values_data_lastupc}, {values_data_stop});")
    conn.commit()

@dp.message_handler(filters.Command('stop'))
async def stop(message: types.Message):
    cur.row_factory = lambda cursor, row: row[0]
    cur.execute(f"SELECT * FROM admins;")
    admins = cur.fetchall()
    if message.from_user.id not in admins:
        await message.answer('Ты не админ!')
        return
    else:
        try:
            cur.execute(f"UPDATE data SET stop = 1")
            conn.commit()
            await message.answer('Парсинг скоро остановится')
        except:
            await message.answer('error')


@dp.message_handler(filters.Command('addadmin'))
async def addadmin(message: types.Message):
    cur.row_factory = lambda cursor, row: row[0]
    cur.execute(f"SELECT * FROM admins;")
    admins = cur.fetchall()
    if message.from_user.id not in admins:
        await message.answer('Ты не админ!')
        return
    else:
        arguments = message.get_args()
        try:
            cur.execute(f"INSERT OR IGNORE INTO admins VALUES ({int(arguments)})")
            conn.commit()
            await message.answer(f'`{arguments}` добавлен в список администраторов', parse_mode='markdown')
        except:
            await message.answer('error')

@dp.message_handler(filters.Command('addchat'))
async def addchat(message: types.Message):
    cur.row_factory = lambda cursor, row: row[0]
    cur.execute(f"SELECT * FROM admins;")
    admins = cur.fetchall()
    if message.from_user.id not in admins:
        await message.answer('Ты не админ!')
        return
    else:
        arguments = message.get_args()
        try:
            cur.execute(f"INSERT OR IGNORE INTO chats VALUES ({int(arguments)})")
            conn.commit()
            await message.answer(f'`{arguments}` добавлен в список чатов', parse_mode='markdown')
        except:
            await message.answer('error')

@dp.message_handler(filters.Command('setupc'))
async def setupc(message: types.Message):
    cur.row_factory = lambda cursor, row: row[0]
    cur.execute(f"SELECT * FROM admins;")
    admins = cur.fetchall()
    if message.from_user.id not in admins:
        await message.answer('Ты не админ!')
        return
    else:
        arguments = message.get_args()
        try:
            cur.execute(f"UPDATE data SET lastupc = '{arguments}'")
            conn.commit()
            await message.answer(f'Новый UPC: `{arguments}`', parse_mode='markdown')
        except:
            await message.answer('error')

@dp.message_handler(filters.Command('getlastupc'))
async def getlastupc(message: types.Message):
    cur.row_factory = lambda cursor, row: row[0]
    cur.execute(f"SELECT * FROM admins;")
    admins = cur.fetchall()
    if message.from_user.id not in admins:
        await message.answer('Ты не админ!')
        return
    else:
        cur.execute(f"SELECT lastupc FROM data;")
        result = cur.fetchone()
        await message.answer(f'Текущий стартовый UPC: `{result}`', parse_mode='markdown')

@dp.message_handler(filters.CommandStart())
async def start(message: types.Message):
    cur.row_factory = lambda cursor, row: row[0]
    cur.execute(f"SELECT * FROM admins;")
    admins = cur.fetchall()
    if message.from_user.id not in admins:
        await message.answer('Ты не админ!')
        return
    else:
        cur.execute(f"SELECT * FROM chats;")
        cur.row_factory = None
        chats = cur.fetchall()
        chatids = []
        for chat in chats:
            chatid = chat[0]
            chatids.append(chatid)
        print(chatids)
        await message.reply(f"*🔥 Привет! Я бот для парсинга релизов с белива\nНачинаю постинг релизов\n🧑‍💻 Разработчик: @clownl3ss*", parse_mode="markdown")
        cur.execute(f"UPDATE data SET stop = 0")
        conn.commit()
        cur.execute(f"SELECT * FROM data;")
        datastring = cur.fetchall()
        for rows in datastring:
            lastupc = rows[0]
        cur.row_factory = lambda cursor, row: row[0]
        for upc in range(lastupc, 999999999999999999):
            cur.row_factory = None
            cur.execute(f"SELECT * FROM data;")
            datastring = cur.fetchall()
            for rows in datastring:
                stop = rows[1]
            if stop == 1:
                await message.answer('Парсинг остановлен!')
                cur.row_factory = lambda cursor, row: row[0]
                break
            elif stop == 0:
                cur.execute(f"SELECT * FROM data;")
                lastupc = cur.fetchall()
                requrl = f'http://player.believe.fr/v2/{upc}'
                coverurl = f'https://covers.believedigital.com/full/{upc}.jpg'
                response = requests.get(requrl)
                soup = BeautifulSoup(response.text, "html.parser")
                f = open('upc.txt', 'w')
                f.write(str(upc))
                f.close()
                title = soup.find("meta", property="og:title")['content']
                author = soup.find("meta", attrs={'name':'author'})['content']
                if author:
                    acrrequrl = f"https://eu-api-v2.acrcloud.com/api/music/search?per_page=1&page=1&q=upc:{upc}"
                    headers = {
                        'Accept': 'application/json',
                        'Authorization': f'Bearer {ACR_BEARER}'
                    }
                    response = requests.get(acrrequrl, headers=headers)
                    data = json.loads(response.text)
                    firstline = f'{author} - {title}'
                    regex = "^[a-zA-Zа-яА-ЯёЁ]+$"
                    pattern = re.compile(regex)
                    antiarab = pattern.search(firstline) is not None
                    try:    
                        album = data["data"][0]["album"]["name"]
                    except:
                        album = "None (нету в акре)"
                    try:
                        label = data["data"][0]["label"]
                    except:
                        label = "None (нету в акре)"
                    try:
                        if antiarab == False:
                            cur.execute(f"UPDATE data SET lastupc = '{upc}';")
                            conn.commit()
                            cur.execute(f"SELECT * FROM chats;")
                            cur.row_factory = None
                            chats = cur.fetchall()
                            chatids = []
                            for chat in chats:
                                chatid = chat[0]
                                await bot.send_photo(chatid, coverurl, f'{firstline}\n\nАльбом: {album}\nUPC: {upc}\nЛейбл: {label}')
                                cur.row_factory = lambda cursor, row: row[0]
                    except:
                        pass

if __name__ == '__main__':
    executor.start_polling(dp)
