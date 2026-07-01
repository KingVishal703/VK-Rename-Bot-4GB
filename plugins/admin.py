from pyrogram.types import (InlineKeyboardButton, InlineKeyboardMarkup)
from config import *
from pyrogram import Client, filters
from helper.date import add_date
from helper.database import (
    uploadlimit,
    usertype,
    addpre,
    set_intro,
    set_intro_file,
    set_outro,
    set_outro_file,
    set_watermark,
    set_watermark_file,
    set_watermark_position,
    set_text_watermark,
    set_text_watermark_status
)



@Client.on_message(filters.private & filters.user(ADMIN) & filters.command(["warn"]))
async def warn(c, m):
    if len(m.command) >= 3:
        try:
            user_id = m.text.split(' ', 2)[1]
            reason = m.text.split(' ', 2)[2]
            await m.reply_text("User Notfied Sucessfully 😁")
            await c.send_message(chat_id=int(user_id), text=reason)
        except:
            await m.reply_text("User Not Notfied Sucessfully 😔")
            
            

@Client.on_message(filters.private & filters.user(ADMIN) & filters.command(["addpremium"]))
async def buypremium(bot, message):
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("🪙 Basic", callback_data="vip1"),
        InlineKeyboardButton("⚡ Standard", callback_data="vip2")],
        [InlineKeyboardButton("💎 Pro", callback_data="vip3")],
        [InlineKeyboardButton("✖️ Cancel ✖️",callback_data = "cancel")]
        ])
        
    await message.reply_text("🦋 Select Plan To Upgrade...", quote=True, reply_markup=button)
    
    

@Client.on_message((filters.channel | filters.private) & filters.user(ADMIN) & filters.command(["ceasepower"]))
async def ceasepremium(bot, message):
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("Limit 1GB", callback_data="cp1"),
        InlineKeyboardButton("All Power Cease", callback_data="cp2")],
        [InlineKeyboardButton("✖️ Cancel ✖️",callback_data = "cancel")]
        ])
	
    await message.reply_text("😁 Power Cease Mode...", quote=True, reply_markup=button)



@Client.on_message((filters.channel | filters.private) & filters.user(ADMIN) & filters.command(["resetpower"]))
async def resetpower(bot, message):
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Yes",callback_data = "dft"),
        InlineKeyboardButton("❌ No",callback_data = "cancel")]
        ])
        
    await message.reply_text(text=f"Do You Really Want To Reset Daily Limit To Default Data Limit 2GB ?", quote=True, reply_markup=button)
    
    
    

# PREMIUM POWER MODE @JISHUDEVELOPER
@Client.on_callback_query(filters.regex('vip1'))
async def vip1(bot,update):
    id = update.message.reply_to_message.text.split("/addpremium")
    user_id = id[1].replace(" ", "")
    inlimit  = 21474836500
    uploadlimit(int(user_id),21474836500)
    usertype(int(user_id),"🪙 Basic")
    addpre(int(user_id))
    await update.message.edit("Added Successfully To Premium Upload Limit 20 GB")
    await bot.send_message(user_id, f"Hey {update.from_user.mention} \n\nYou Are Upgraded To <b>🪙 Basic</b>. Check Your Plan Here /myplan")



@Client.on_callback_query(filters.regex('vip2'))
async def vip2(bot,update):
    id = update.message.reply_to_message.text.split("/addpremium")
    user_id = id[1].replace(" ", "")
    inlimit = 53687091200
    uploadlimit(int(user_id), 53687091200)
    usertype(int(user_id),"⚡ Standard")
    addpre(int(user_id))
    await update.message.edit("Added Successfully To Premium Upload Limit 50 GB")
    await bot.send_message(user_id, f"Hey {update.from_user.mention} \n\nYou Are Upgraded To <b>⚡ Standard</b>. Check Your Plan Here /myplan")



@Client.on_callback_query(filters.regex('vip3'))
async def vip3(bot,update):
    id = update.message.reply_to_message.text.split("/addpremium")
    user_id = id[1].replace(" ", "")
    inlimit = 107374182400
    uploadlimit(int(user_id), 107374182400)
    usertype(int(user_id),"💎 Pro")
    addpre(int(user_id))
    await update.message.edit("Added Successfully To Premium Upload Limit 100 GB")
    await bot.send_message(user_id, f"Hey {update.from_user.mention} \n\nYou Are Upgraded To <b>💎 Pro</b>. Check Your Plan Here /myplan")





# CEASE POWER MODE @JISHUDEVELOPER
@Client.on_callback_query(filters.regex('cp1'))
async def cp1(bot,update):
    id = update.message.reply_to_message.text.split("/ceasepower")
    user_id = id[1].replace(" ", "")
    inlimit  = 2147483652
    uploadlimit(int(user_id), 2147483652)
    usertype(int(user_id),"⚠️ Account Downgraded")
    addpre(int(user_id))
    await update.message.edit("Added Successfully To Upload Limit 2GB")
    await bot.send_message(user_id, f"Hey {update.from_user.mention} \n\nYou Are Downgraded To Cease <b>Limit 2GB</b>. Check Your Plan Here /myplan \n\n<b>Contact Admin :</b> @MadflixOfficials")



@Client.on_callback_query(filters.regex('cp2'))
async def cp2(bot,update):
    id = update.message.reply_to_message.text.split("/ceasepower")
    user_id = id[1].replace(" ", "")
    inlimit  = 0
    uploadlimit(int(user_id), 0)
    usertype(int(user_id),"⚠️ Account Downgraded")
    addpre(int(user_id))
    await update.message.edit("Added Successfully To Upload Limit 0GB")
    await bot.send_message(user_id, f"Hey {update.from_user.mention} \n\nYou Are Downgraded To Cease <b>Limit 0GB</b>. Check Your Plan Here /myplan \n\n<b>Contact Admin :</b> @MadflixOfficials")




# RESET POWER MODE @JISHUDEVELOPER
@Client.on_callback_query(filters.regex('dft'))
async def dft(bot,update):
    id = update.message.reply_to_message.text.split("/resetpower")
    user_id = id[1].replace(" ", "")
    inlimit = 2147483652
    uploadlimit(int(user_id), 2147483652)
    usertype(int(user_id),"🆓 Free")
    addpre(int(user_id))
    await update.message.edit("Daily Data Limit Has Been Reset Successfully.\n\nThis Account Has Default 2GB Remaining Capacity")
    await bot.send_message(user_id, f"Hey {update.from_user.mention} \n\nYour Daily Data Limit Has Been Reset Successfully. Check Your Plan Here /myplan\n\n<b>Contact Admin :</b> @MadflixOfficials")


# ================= VIDEO EDIT SETTINGS ================= #

@Client.on_message(filters.private & filters.user(ADMIN) & filters.command("intro"))
async def intro_toggle(client, message):

    if len(message.command) != 2:
        return await message.reply("Usage:\n/intro on\n/intro off")

    if message.command[1].lower() == "on":
        set_intro(message.chat.id, True)
        await message.reply("✅ Intro Enabled")

    else:
        set_intro(message.chat.id, False)
        await message.reply("❌ Intro Disabled")


@Client.on_message(filters.private & filters.user(ADMIN) & filters.command("outro"))
async def outro_toggle(client, message):

    if len(message.command) != 2:
        return await message.reply("Usage:\n/outro on\n/outro off")

    if message.command[1].lower() == "on":
        set_outro(message.chat.id, True)
        await message.reply("✅ Outro Enabled")

    else:
        set_outro(message.chat.id, False)
        await message.reply("❌ Outro Disabled")


@Client.on_message(filters.private & filters.user(ADMIN) & filters.command("watermark"))
async def watermark_toggle(client, message):

    if len(message.command) != 2:
        return await message.reply("Usage:\n/watermark on\n/watermark off")

    if message.command[1].lower() == "on":
        set_watermark(message.chat.id, True)
        await message.reply("✅ Watermark Enabled")

    else:
        set_watermark(message.chat.id, False)
        await message.reply("❌ Watermark Disabled")


@Client.on_message(filters.private & filters.user(ADMIN) & filters.command("text"))
async def text_toggle(client, message):

    if len(message.command) != 2:
        return await message.reply("Usage:\n/text on\n/text off")

    if message.command[1].lower() == "on":
        set_text_watermark_status(message.chat.id, True)
        await message.reply("✅ Text Watermark Enabled")

    else:
        set_text_watermark_status(message.chat.id, False)
        await message.reply("❌ Text Watermark Disabled")


@Client.on_message(filters.private & filters.user(ADMIN) & filters.command("setintro"))
async def set_intro_video(client, message):

    if not message.reply_to_message:
        return await message.reply("❌ Reply to a video/gif for intro")

    file_id = message.reply_to_message.video or message.reply_to_message.document or message.reply_to_message.animation

    if not file_id:
        return await message.reply("❌ Invalid file")

    set_intro_file(message.chat.id, file_id.file_id)
    set_intro(message.chat.id, True)

    await message.reply("✅ Intro video saved successfully")

@Client.on_message(filters.private & filters.user(ADMIN) & filters.command("setoutro"))
async def set_outro_video(client, message):

    if not message.reply_to_message:
        return await message.reply("❌ Reply to a video/gif for outro")

    file_id = message.reply_to_message.video or message.reply_to_message.document or message.reply_to_message.animation

    if not file_id:
        return await message.reply("❌ Invalid file")

    set_outro_file(message.chat.id, file_id.file_id)
    set_outro(message.chat.id, True)

    await message.reply("✅ Outro video saved successfully")



@Client.on_message(filters.private & filters.user(ADMIN) & filters.command("setwatermark"))
async def set_watermark_image(client, message):

    if not message.reply_to_message:
        return await message.reply("❌ Reply to an image")

    file_id = message.reply_to_message.photo

    if not file_id:
        return await message.reply("❌ Invalid image")

    set_watermark_file(message.chat.id, file_id.file_id)
    set_watermark(message.chat.id, True)

    await message.reply("✅ Watermark image saved successfully")


@Client.on_message(filters.private & filters.user(ADMIN) & filters.command("settext"))
async def set_text_watermark_cmd(client, message):

    if len(message.command) < 2:
        return await message.reply("Usage: /settext your_text_here")

    text = message.text.split(" ", 1)[1]

    set_text_watermark(message.chat.id, text)
    set_text_watermark_status(message.chat.id, True)

    await message.reply(f"✅ Text watermark saved:\n{text}")
# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Back-Up Channel @JishuBotz
# Developer @JishuDeveloper & @MadflixOfficials
