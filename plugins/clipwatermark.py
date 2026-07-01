import os
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from helper.database import (
    set_intro, del_intro, set_outro, del_outro,
    set_watermark, del_watermark,
    set_clips_toggle, set_watermark_toggle,
    get_clip_settings,
)

CLIPS_DIR = "clips"
if not os.path.isdir(CLIPS_DIR):
    os.mkdir(CLIPS_DIR)


def _settings_text(s):
    return (
        "**🎬 Intro/Outro & Watermark Settings**\n\n"
        f"**Intro Clip :-** {'✅ Set' if s['intro_path'] else '❌ Not Set'}\n"
        f"**Outro Clip :-** {'✅ Set' if s['outro_path'] else '❌ Not Set'}\n"
        f"**Watermark :-** {'✅ Set' if s['watermark_path'] else '❌ Not Set'}\n\n"
        "Set files using /setintro , /setoutro (reply to a video) and "
        "/setwatermark (reply to a photo).\n\n"
        "Then turn the features **On/Off** below 👇"
    )


def _settings_markup(s):
    clips_btn = InlineKeyboardButton(
        f"Clips {'✅ ON' if s['clips_enabled'] else '❌ OFF'}",
        callback_data="clipset_clips_toggle",
    )
    wm_btn = InlineKeyboardButton(
        f"Watermark {'✅ ON' if s['watermark_enabled'] else '❌ OFF'}",
        callback_data="clipset_wm_toggle",
    )
    return InlineKeyboardMarkup([[clips_btn], [wm_btn], [InlineKeyboardButton("✖️ Close", callback_data="cancel")]])


# ---------------- SET INTRO ---------------- #

@Client.on_message(filters.private & filters.command("setintro") & filters.reply)
async def setintro(client, message: Message):
    reply = message.reply_to_message
    media = reply.video or reply.document
    if not media:
        return await message.reply_text("❌ Reply To A Video File With /setintro")
    ms = await message.reply_text("⬇️ Saving Intro Clip...")
    local_path = os.path.join(CLIPS_DIR, f"{message.chat.id}_intro.mp4")
    if os.path.exists(local_path):
        os.remove(local_path)
    path = await client.download_media(reply, file_name=local_path)
    set_intro(message.chat.id, media.file_id, path)
    await ms.edit("✅ Intro Clip Saved Successfully.\n\nDon't forget to turn it **ON** via /clipsettings")


@Client.on_message(filters.private & filters.command("setintro") & ~filters.reply)
async def setintro_noreply(client, message: Message):
    await message.reply_text("❌ Reply To A Video File With /setintro")


@Client.on_message(filters.private & filters.command("delintro"))
async def delintro(client, message: Message):
    s = get_clip_settings(message.chat.id)
    if s["intro_path"] and os.path.exists(s["intro_path"]):
        try:
            os.remove(s["intro_path"])
        except Exception:
            pass
    del_intro(message.chat.id)
    await message.reply_text("🗑️ Intro Clip Deleted Successfully.")


# ---------------- SET OUTRO ---------------- #

@Client.on_message(filters.private & filters.command("setoutro") & filters.reply)
async def setoutro(client, message: Message):
    reply = message.reply_to_message
    media = reply.video or reply.document
    if not media:
        return await message.reply_text("❌ Reply To A Video File With /setoutro")
    ms = await message.reply_text("⬇️ Saving Outro Clip...")
    local_path = os.path.join(CLIPS_DIR, f"{message.chat.id}_outro.mp4")
    if os.path.exists(local_path):
        os.remove(local_path)
    path = await client.download_media(reply, file_name=local_path)
    set_outro(message.chat.id, media.file_id, path)
    await ms.edit("✅ Outro Clip Saved Successfully.\n\nDon't forget to turn it **ON** via /clipsettings")


@Client.on_message(filters.private & filters.command("setoutro") & ~filters.reply)
async def setoutro_noreply(client, message: Message):
    await message.reply_text("❌ Reply To A Video File With /setoutro")


@Client.on_message(filters.private & filters.command("deloutro"))
async def deloutro(client, message: Message):
    s = get_clip_settings(message.chat.id)
    if s["outro_path"] and os.path.exists(s["outro_path"]):
        try:
            os.remove(s["outro_path"])
        except Exception:
            pass
    del_outro(message.chat.id)
    await message.reply_text("🗑️ Outro Clip Deleted Successfully.")


# ---------------- SET WATERMARK ---------------- #

@Client.on_message(filters.private & filters.command("setwatermark") & filters.reply)
async def setwatermark(client, message: Message):
    reply = message.reply_to_message
    if not reply.photo:
        return await message.reply_text("❌ Reply To A Photo/Image With /setwatermark")
    ms = await message.reply_text("⬇️ Saving Watermark...")
    local_path = os.path.join(CLIPS_DIR, f"{message.chat.id}_watermark.png")
    if os.path.exists(local_path):
        os.remove(local_path)
    path = await client.download_media(reply, file_name=local_path)
    set_watermark(message.chat.id, reply.photo.file_id, path)
    await ms.edit("✅ Watermark Saved Successfully.\n\nDon't forget to turn it **ON** via /clipsettings")


@Client.on_message(filters.private & filters.command("setwatermark") & ~filters.reply)
async def setwatermark_noreply(client, message: Message):
    await message.reply_text("❌ Reply To A Photo/Image With /setwatermark")


@Client.on_message(filters.private & filters.command("delwatermark"))
async def delwatermark(client, message: Message):
    s = get_clip_settings(message.chat.id)
    if s["watermark_path"] and os.path.exists(s["watermark_path"]):
        try:
            os.remove(s["watermark_path"])
        except Exception:
            pass
    del_watermark(message.chat.id)
    await message.reply_text("🗑️ Watermark Deleted Successfully.")


# ---------------- SETTINGS / TOGGLES ---------------- #

@Client.on_message(filters.private & filters.command("clipsettings"))
async def clipsettings(client, message: Message):
    s = get_clip_settings(message.chat.id)
    await message.reply_text(_settings_text(s), reply_markup=_settings_markup(s))


@Client.on_callback_query(filters.regex("^clipset_"))
async def clipsettings_callback(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    s = get_clip_settings(chat_id)

    if query.data == "clipset_clips_toggle":
        if not s["intro_path"] and not s["outro_path"]:
            return await query.answer("⚠️ Set an intro or outro clip first with /setintro or /setoutro", show_alert=True)
        set_clips_toggle(chat_id, not s["clips_enabled"])

    elif query.data == "clipset_wm_toggle":
        if not s["watermark_path"]:
            return await query.answer("⚠️ Set a watermark first with /setwatermark", show_alert=True)
        set_watermark_toggle(chat_id, not s["watermark_enabled"])

    s = get_clip_settings(chat_id)
    await query.message.edit_text(_settings_text(s), reply_markup=_settings_markup(s))
    await query.answer()


# Jishu Developer
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Back-Up Channel @JishuBotz
# Developer @JishuDeveloper & @MadflixOfficials
