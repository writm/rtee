import feedparser
import asyncio
import os
import requests
from bs4 import BeautifulSoup
from telegram.ext import ApplicationBuilder

# Load config from environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
SUBSCRIPTION_LINK = os.getenv('SUBSCRIPTION_LINK', 'https://t.me/+7E9osI2t45k0NWMy')

sent_news_ids = set()

async def fetch_latest_news():
    rss_url = 'https://www.dailymail.co.uk/articles.rss'
    feed = feedparser.parse(rss_url)
    latest_news = feed.entries[0]
    return latest_news.title, latest_news.description, latest_news.link, latest_news.id

def get_original_image(link):
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        image_tag = soup.find('meta', property='og:image')
        if image_tag:
            return image_tag['content']
        image_tag = soup.find('img')
        if image_tag and 'src' in image_tag.attrs:
            return image_tag['src']
    except Exception as e:
        print(f"Image fetch error: {e}")
    return None

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

async def run_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    title, description, link, news_id = await fetch_latest_news()

    if news_id not in sent_news_ids:
        original_image_url = get_original_image(link)
        await send_to_telegram(app, title, description, original_image_url)
        sent_news_ids.add(news_id)

async def main():
    while True:
        await run_bot()
        await asyncio.sleep(1800)  # 30 minutes

if __name__ == '__main__':
    asyncio.run(main())
