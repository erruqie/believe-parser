import os
import json
import logging
import requests

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from aiogram.utils import executor
from aiogram import Bot, types, filters
from aiogram.dispatcher import Dispatcher

load_dotenv('.env')
logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.environ.get('BOT_TOKEN'))
dp = Dispatcher(bot)
RELEASES_CHANNEL = os.environ.get('RELEASES_CHANNEL')
ACR_BEARER = os.environ.get('ACR_BEARER')

@dp.message_handler(filters.CommandStart())
async def start(message: types.Message):
    await message.reply(f"*🔥 Привет! Я бот для парсинга релизов с белива\nНачинаю постинг релизов в канал с ID `{RELEASES_CHANNEL}`\n🧑‍💻 Разработчик: @clownl3ss*", parse_mode="markdown")
    for upc in range(3616849175761, 999999999999999999):
        requrl = f'http://player.believe.fr/v2/{upc}'
        coverurl = f'https://covers.believedigital.com/full/{upc}.jpg'
        response = requests.get(requrl)
        soup = BeautifulSoup(response.text, "html.parser")
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
            try:
                date = data["data"][0]["release_date"]
            except:
                date = "None (нету в акре)"
            if date == "":
                date = "None (нету в акре)"
            try:    
                album = data["data"][0]["album"]["name"]
            except:
                album = "None (нету в акре)"
            try:
                label = data["data"][0]["label"]
            except:
                label = "None (нету в акре)"
            try:
                await bot.send_photo(RELEASES_CHANNEL, coverurl, f'{author} - {title}\n\nДата релиза: {date}\nАльбом: {album}\nUPC: {upc}\nЛейбл: {label}')
            except:
                pass


if __name__ == '__main__':
    executor.start_polling(dp)