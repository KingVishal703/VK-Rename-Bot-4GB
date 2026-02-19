from pyrogram import Client, idle
from plugins.cb_data import app as Client2
from config import *
import pyromod
import pyrogram.utils
import threading
from flask import Flask

pyrogram.utils.MIN_CHAT_ID = -999999999999
pyrogram.utils.MIN_CHANNEL_ID = -100999999999999

bot = Client(
    "Renamer",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
    plugins=dict(root='plugins')
)

# -------------------- FLASK SERVER FOR KOYEB --------------------

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Bot is running!"

def run_web():
    web_app.run(host="0.0.0.0", port=8000)

# ---------------------------------------------------------------

if STRING_SESSION:
    apps = [Client2, bot]

    for app in apps:
        app.start()

    # Start Flask in background thread
    threading.Thread(target=run_web).start()

    idle()

    for app in apps:
        app.stop()

else:
    # Start Flask in background thread
    threading.Thread(target=run_web).start()

    bot.run()


# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Back-Up Channel @JishuBotz
# Developer @JishuDeveloper
