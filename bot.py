import os
import discord
from discord.ext import tasks
import requests
from bs4 import BeautifulSoup

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
TWITCH_USERNAME = os.getenv("TWITCH_USERNAME")

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

last_title = None

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    check_title.start()

@tasks.loop(seconds=60)
async def check_title():
    global last_title
    url = f"https://www.twitch.tv/{TWITCH_USERNAME}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    title_tag = soup.find("meta", property="og:title")

    if title_tag:
        current_title = title_tag["content"]
        if last_title is None:
            last_title = current_title
        elif current_title != last_title:
            last_title = current_title
            channel = await bot.fetch_channel(CHANNEL_ID)
            await channel.send(f"🔔 {TWITCH_USERNAME} updated their stream title:\n> {current_title}")

bot.run(TOKEN)
