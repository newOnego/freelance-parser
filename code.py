import requests, asyncio, os, re
from config import *
from aiogram import *
from lxml import html
from database import *
from datetime import datetime
initDB()

bot = Bot(token = token)
dp = Dispatcher(bot)
deleteInfo()

# Обновление статистики в Telegram.
async def updateMessage():
	while True:
		await asyncio.sleep(5)
		await bot.edit_message_text(chat_id = channel, message_id = "4", text = "Статитика по парсеру:\n- Данные обновлены: " + datetime.now().strftime("%d.%m.%Y, %H:%M:%S") + ";\n- Обработано: " + verificationRequests() + " раз(-а);\n- Трафик: " + str(float(round(int(verificationTraffic()) / 1024 / 1024 / 1024, 2))) + " ГБ.")
		await asyncio.sleep(5)

async def parser():
	print("Парсер запущен!")
	while True:
		try:
			response = requests.get("https://freelance.habr.com/tasks")
			tree = html.fromstring(response.text)
			# Получение размера запроса.
			with open("file.html", "w") as f:
				f.write(response.text)
				f.close()
			size = os.path.getsize("file.html")

			# Пути к атрибутам.
			orderTitle = tree.xpath("//*[@id='tasks_list']/li[1]/article/div/header/div[1]/a/text()")[0]
			orderPrice = tree.xpath("//*[@id='tasks_list']/li[1]/article/aside/div/span/text()")[0]
			orderLink = tree.xpath("//*[@id='tasks_list']/li[1]/article/div/header/div[1]/a/@href")[0]
			
			# Добавление записей, если их нет в БД.
			if verificationInfo() == None:
				addingInfo(link = orderLink)
			if verificationRequests() == None:
				addingStatistics(requests = 0, traffic = 0, id = 1)
			# Добавление информации для статистики.
			updateStatistics(requests = 1 + int(verificationRequests()), traffic = size + int(verificationTraffic()), id = 1)
			
			# Обновление записей в БД.
			if orderLink != verificationInfo():
				deleteInfo()
				addingInfo(link = orderLink)
				# Обработка цены.
				if orderPrice == "договорная":
					orderPrice = orderPrice + "."
				else:
					orderPrice = orderPrice + tree.xpath("//*[@id='tasks_list']/li[1]/article/aside/div/span/span/text()")[0] + "."
				# Отправка сообщения в Telegram.
				keyboard = types.InlineKeyboardMarkup()
				keyboard.add(types.InlineKeyboardButton(text = "Перейти к заказу!", url = "https://freelance.habr.com" + orderLink))
				await bot.send_message(channel, "Новый заказ: \"" + re.sub(r"^\s+|\s+$", "", orderTitle.replace("  ", " ")) + "\". Цена: " + orderPrice, reply_markup = keyboard)
			await asyncio.sleep(1)
		except IndexError:
			print("Возникла ошибка при получении данных со страницы.")
			continue

async def work():
	await asyncio.gather(updateMessage(), parser())
asyncio.run(work())