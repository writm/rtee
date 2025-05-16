import feedparser
import asyncio
from telegram.ext import ApplicationBuilder
from background import keep_alive
import threading
import pip
import requests
from bs4 import BeautifulSoup

# Установка необходимых библиотек
pip.main(['install', 'pytelegrambotapi', 'beautifulsoup4', 'requests'])

# Замените на ваш токен Telegram и ID канала
TELEGRAM_TOKEN = '8165234385:AAELS2kZmZUgk5r4F8GHeJT5jbsE3LASjic'
CHANNEL_ID = '@GlobalNewsPulse'
SUBSCRIPTION_LINK = 'https://t.me/+7E9osI2t45k0NWMy'

# Множество для хранения идентификаторов отправленных новостей
sent_news_ids = set()

async def fetch_latest_news():
    rss_url = 'https://www.dailymail.co.uk/articles.rss'
    feed = feedparser.parse(rss_url)

    # Получаем первую новость
    latest_news = feed.entries[0]

    title = latest_news.title
    description = latest_news.description
    link = latest_news.link  # Ссылка на основную новость
    news_id = latest_news.id  # Предполагаем, что у каждой новости есть уникальный идентификатор

    return title, description, link, news_id

def get_original_image(link):
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Попробуем найти оригинальное изображение
        image_tag = soup.find('meta', property='og:image')  # Используем Open Graph
        if image_tag:
            return image_tag['content']

        # Если не нашли, попробуем найти в других тегах
        image_tag = soup.find('img')
        if image_tag and 'src' in image_tag.attrs:
            return image_tag['src']

    except Exception as e:
        print(f"Ошибка при получении изображения: {e}")

    return None  # Если изображение не найдено

async def send_to_telegram(app, title, description, image_url):
    message = (
        f"<b>{title}</b>\n\n"
        f"{description}\n\n"
        f"<a href='{SUBSCRIPTION_LINK}'>Breaking News Now. SUBSCRIBE</a>"
    )

    if image_url:
        await app.bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption=message, parse_mode='HTML')
    else:
        await app.bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode='HTML')

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    while True:
        title, description, link, news_id = await fetch_latest_news()

        # Проверяем, была ли новость уже отправлена
        if news_id not in sent_news_ids:
            original_image_url = get_original_image(link)  # Получаем оригинальную картинку
            await send_to_telegram(app, title, description, original_image_url)
            sent_news_ids.add(news_id)  # Добавляем идентификатор новости в множество

        await asyncio.sleep(1800)  # Задержка в 60 секунд

if __name__ == '__main__':
    # Запускаем Flask сервер в отдельном потоке
    threading.Thread(target=keep_alive).start()
    asyncio.run(main())
