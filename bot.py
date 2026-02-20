from pyrogram import Client, idle
from plugins.cb_data import app as Client2
from config import *
import pyromod
import pyrogram.utils
import threading
from flask import Flask
import os

pyrogram.utils.MIN_CHAT_ID = -999999999999
pyrogram.utils.MIN_CHANNEL_ID = -100999999999999

bot = Client(
    "Renamer",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
    plugins=dict(root='plugins')
)

# -------------------- FLASK SERVER --------------------

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 8000))
    web_app.run(host="0.0.0.0", port=port)

# Flask ko sirf ek baar start karo
threading.Thread(target=run_web, daemon=True).start()

# -------------------- BOT START --------------------

if STRING_SESSION:
    apps = [Client2, bot]
    for app in apps:
        app.start()

    idle()

    for app in apps:
        app.stop()

else:
    bot.run()


# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Back-Up Channel @JishuBotz
# Developer @JishuDeveloper
