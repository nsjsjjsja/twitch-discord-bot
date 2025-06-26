import discord
import aiohttp
import asyncio
import os
from flask import Flask
from threading import Thread

# Mini web server to keep Replit alive
app = Flask('')
@app.route('/')
def home():
    return "Bot is alive!"
def run():
    app.run(host='0.0.0.0', port=8080)
def keep_alive():
    Thread(target=run).start()

# Load environment variables
TOKEN = os.environ["TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])
TWITCH_USERNAME = "jasontheween"
TWITCH_CLIENT_ID = os.environ["TWITCH_CLIENT_ID"]
TWITCH_CLIENT_SECRET = os.environ["TWITCH_CLIENT_SECRET"]

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

access_token = None
last_title = None

async def get_twitch_token():
    global access_token
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params) as resp:
            data = await resp.json()
            access_token = data["access_token"]

async def get_stream_data():
    url = f"https://api.twitch.tv/helix/streams?user_login={TWITCH_USERNAME}"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {access_token}"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            return await resp.json()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await get_twitch_token()
    bot.loop.create_task(check_title_loop())

async def check_title_loop():
    global last_title
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)
    while not bot.is_closed():
        try:
            data = await get_stream_data()
            if data["data"]:
                current_title = data["data"][0]["title"]
                if current_title != last_title:
                    last_title = current_title
                    await channel.send(f"🔴 {TWITCH_USERNAME} changed stream title to:\n> **{current_title}**")
        except Exception as e:
            print(f"Error: {e}")
        await asyncio.sleep(60)

keep_alive()
bot.run(TOKEN)

