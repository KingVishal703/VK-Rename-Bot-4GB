from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyromod.exceptions import ListenerTimeout
from helper.database import (
    get_extras, set_intro, set_outro, del_intro, del_outro,
    toggle_intro, toggle_outro, set_watermark_text, set_watermark_image,
    del_watermark, toggle_watermark,
)
import os

EXTRAS_DIR = "data/extras"
os.makedirs(EXTRAS_DIR, exist_ok=True)


def settings_markup(ex):
    intro_btn = InlineKeyboardButton(
        f"Intro {'✅ ON' if ex['intro_enabled'] else '❌ OFF'}",
        callback_data=f"ex_introtoggle_{0 if ex['intro_enabled'] else 1}",
    )
    outro_btn = InlineKeyboardButton(
        f"Outro {'✅ ON' if ex['outro_enabled'] else '❌ OFF'}",
        callback_data=f"ex_outrotoggle_{0 if ex['outro_enabled'] else 1}",
    )
    wm_btn = InlineKeyboardButton(
        f"Watermark {'✅ ON' if ex['watermark_enabled'] else '❌ OFF'}",
        callback_data=f"ex_wmtoggle_{0 if ex['watermark_enabled'] else 1}",
    )
    return InlineKeyboardMarkup([[intro_btn], [outro_btn], [wm_btn]])


@Client.on_message(filters.private & filters.command("videosettings"))
async def video_settings(client, message: Message):
    ex = get_extras(message.chat.id)
    wm_status = "Not set ❌"
    if ex["watermark_type"] == "text":
        wm_status = f"Text ✅ (`{ex['watermark_text']}`)"
    elif ex["watermark_type"] == "image":
        wm_status = "Image ✅"

    text = (
        "🎬 **Video Extras Settings**\n\n"
        f"▫️ Intro clip: {'Set ✅' if ex['intro_path'] else 'Not set ❌'}\n"
        f"▫️ Outro clip: {'Set ✅' if ex['outro_path'] else 'Not set ❌'}\n"
        f"▫️ Watermark: {wm_status}\n\n"
        "Neeche buttons se ON/OFF karo (jab tak set na ho tab tak ON nahi hoga).\n\n"
        "Naya set karne ke liye:\n"
        "`/setintro` — video reply karke\n"
        "`/setoutro` — video reply karke\n"
        "`/setwatermark` — text ya image select karo"
    )
    await message.reply_text(text, reply_markup=settings_markup(ex))


@Client.on_callback_query(filters.regex(r"^ex_introtoggle_"))
async def cb_intro_toggle(client, query: CallbackQuery):
    ex = get_extras(query.message.chat.id)
    if not ex["intro_path"]:
        return await query.answer("Pehle /setintro se intro clip set karo!", show_alert=True)
    enable = query.data.split("_")[-1] == "1"
    toggle_intro(query.message.chat.id, enable)
    ex = get_extras(query.message.chat.id)
    await query.message.edit_reply_markup(settings_markup(ex))
    await query.answer("Intro " + ("ON ✅" if enable else "OFF ❌"))


@Client.on_callback_query(filters.regex(r"^ex_outrotoggle_"))
async def cb_outro_toggle(client, query: CallbackQuery):
    ex = get_extras(query.message.chat.id)
    if not ex["outro_path"]:
        return await query.answer("Pehle /setoutro se outro clip set karo!", show_alert=True)
    enable = query.data.split("_")[-1] == "1"
    toggle_outro(query.message.chat.id, enable)
    ex = get_extras(query.message.chat.id)
    await query.message.edit_reply_markup(settings_markup(ex))
    await query.answer("Outro " + ("ON ✅" if enable else "OFF ❌"))


@Client.on_callback_query(filters.regex(r"^ex_wmtoggle_"))
async def cb_wm_toggle(client, query: CallbackQuery):
    ex = get_extras(query.message.chat.id)
    if not ex["watermark_type"]:
        return await query.answer("Pehle /setwatermark se watermark set karo!", show_alert=True)
    enable = query.data.split("_")[-1] == "1"
    toggle_watermark(query.message.chat.id, enable)
    ex = get_extras(query.message.chat.id)
    await query.message.edit_reply_markup(settings_markup(ex))
    await query.answer("Watermark " + ("ON ✅" if enable else "OFF ❌"))

#first real command
"""@Client.on_message(filters.private & filters.command("setintro"))
async def set_intro_cmd(client, message: Message):
    target = message.reply_to_message
    if not target or not (target.video or target.document or target.animation):
        return await message.reply_text(
            "❗️ Kisi video ko reply karke `/setintro` bhejo.\n\n"
            "Example: Intro clip video bot ko bhejo, us par reply karke `/setintro` type karo."
        )
    ms = await message.reply_text("⬇️ Intro clip download ho rahi hai...")
    path = os.path.join(EXTRAS_DIR, f"{message.chat.id}_intro.mp4")
    try:
        await client.download_media(target, file_name=path)
    except Exception as e:
        return await ms.edit(f"❌ Download fail ho gaya: {e}")
    set_intro(message.chat.id, path)
    await ms.edit(
        "✅ Intro clip set ho gayi!\n\n"
        "Ise apne renamed videos mein ON karne ke liye /videosettings use karo."
    )
"""

#second test command
"""@Client.on_message(filters.private & filters.command("setintro"))
async def set_intro_cmd(client, message: Message):

    # Reply check
    if not message.reply_to_message:
        return await message.reply_text(
            "❌ Kisi video ko reply karke /setintro bhejo."
        )

    target = message.reply_to_message

    # Sirf video allow
    if not (target.video or target.document or target.animation):
        return await message.reply_text(
            "❌ Reply kiya hua message video nahi hai."
        )

    msg = await message.reply_text("⬇️ Intro clip download ho rahi hai...")

    path = os.path.join(EXTRAS_DIR, f"{message.chat.id}_intro.mp4")

    try:
        await target.download(file_name=path)
    except Exception as e:
        return await msg.edit(f"❌ Download failed:\n`{e}`")

    if not os.path.exists(path):
        return await msg.edit("❌ Video download nahi hui.")

    try:
        set_intro(message.chat.id, path)
        toggle_intro(message.chat.id, True)
    except Exception as e:
        return await msg.edit(f"❌ Database Error:\n`{e}`")

    await msg.edit(
        "✅ Intro clip successfully set ho gayi.\n\n"
        "Ab har renamed video ke start me ye intro add hoga."
    )"""

#third test command 

@Client.on_message(filters.private & filters.command("setintro"))
async def set_intro_cmd(client, message: Message):

    try:
        video_msg = await client.ask(
            chat_id=message.chat.id,
            text="🎬 Ab 2 minute ke andar intro video bhejo.",
            filters=filters.video | filters.document | filters.animation,
            timeout=120
        )
    except ListenerTimeout:
        return await message.reply_text(
            "⏰ Time out ho gaya.\nDobara /setintro bhejkar try karo."
        )

    ms = await message.reply_text("⬇️ Intro clip download ho rahi hai...")

    path = os.path.join(EXTRAS_DIR, f"{message.chat.id}_intro.mp4")

    try:
        await client.download_media(video_msg, file_name=path)
    except Exception as e:
        return await ms.edit(f"❌ Download fail ho gaya:\n`{e}`")

    set_intro(message.chat.id, path)
    toggle_intro(message.chat.id, True)

    await ms.edit(
        "✅ Intro clip successfully set ho gayi!\n\n"
        "Ab ye renamed videos me automatically use hogi."
    )





"""@Client.on_message(filters.private & filters.command("setoutro"))
async def set_outro_cmd(client, message: Message):
    target = message.reply_to_message
    if not target or not (target.video or target.document or target.animation):
        return await message.reply_text(
            "❗️ Kisi video ko reply karke `/setoutro` bhejo.\n\n"
            "Example: Outro clip video bot ko bhejo, us par reply karke `/setoutro` type karo."
        )
    ms = await message.reply_text("⬇️ Outro clip download ho rahi hai...")
    path = os.path.join(EXTRAS_DIR, f"{message.chat.id}_outro.mp4")
    try:
        await client.download_media(target, file_name=path)
    except Exception as e:
        return await ms.edit(f"❌ Download fail ho gaya: {e}")
    set_outro(message.chat.id, path)
    await ms.edit(
        "✅ Outro clip set ho gayi!\n\n"
        "Ise apne renamed videos mein ON karne ke liye /videosettings use karo."
    )"""


@Client.on_message(filters.private & filters.command("setoutro"))
async def set_outro_cmd(client, message: Message):

    try:
        video_msg = await client.ask(
            chat_id=message.chat.id,
            text="🎬 Ab 2 minute ke andar outro video bhejo.",
            filters=filters.video | filters.document | filters.animation,
            timeout=120
        )
    except ListenerTimeout:
        return await message.reply_text(
            "⏰ Time out ho gaya.\nDobara /setoutro bhejkar try karo."
        )

    ms = await message.reply_text("⬇️ Outro clip download ho rahi hai...")

    path = os.path.join(EXTRAS_DIR, f"{message.chat.id}_outro.mp4")

    try:
        await client.download_media(video_msg, file_name=path)
    except Exception as e:
        return await ms.edit(f"❌ Download fail ho gaya:\n`{e}`")

    set_outro(message.chat.id, path)
    toggle_outro(message.chat.id, True)

    await ms.edit(
        "✅ Outro clip successfully set ho gayi!\n\n"
        "Ab ye renamed videos ke end me automatically use hogi."
    )


@Client.on_message(filters.private & filters.command("removeintro"))
async def remove_intro_cmd(client, message: Message):
    ex = get_extras(message.chat.id)
    if ex["intro_path"] and os.path.exists(ex["intro_path"]):
        try:
            os.remove(ex["intro_path"])
        except Exception:
            pass
    del_intro(message.chat.id)
    await message.reply_text("🗑️ Intro clip remove kar di gayi.")


@Client.on_message(filters.private & filters.command("removeoutro"))
async def remove_outro_cmd(client, message: Message):
    ex = get_extras(message.chat.id)
    if ex["outro_path"] and os.path.exists(ex["outro_path"]):
        try:
            os.remove(ex["outro_path"])
        except Exception:
            pass
    del_outro(message.chat.id)
    await message.reply_text("🗑️ Outro clip remove kar di gayi.")


@Client.on_message(filters.private & filters.command("setwatermark"))
async def set_watermark_cmd(client, message: Message):
    buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton("✍️ Text", callback_data="ex_wm_settext"),
        InlineKeyboardButton("🖼 Image", callback_data="ex_wm_setimage"),
    ]])
    await message.reply_text("Watermark kis type ka set karna hai?", reply_markup=buttons)


@Client.on_callback_query(filters.regex(r"^ex_wm_set(text|image)$"))
async def set_watermark_type_cb(client, query: CallbackQuery):
    kind = query.data[len("ex_wm_set"):]  # "text" or "image"
    chat_id = query.message.chat.id
    await query.message.delete()

    try:
        if kind == "text":
            asked = await client.ask(
                chat_id=chat_id,
                text="✍️ Watermark ke liye text bhejo (jaise `@YourChannel`):",
                filters=filters.text,
                timeout=60,
            )
            set_watermark_text(chat_id, asked.text)
            toggle_watermark(chat_id, True)
            await asked.reply_text(
                "✅ Text watermark set ho gaya aur ON kar diya gaya hai!\n\n"
                "/videosettings se OFF/ON control karo."
            )
        else:
            asked = await client.ask(
                chat_id=chat_id,
                text="🖼 Watermark ke liye ek image bhejo (transparent PNG logo best rahega):",
                filters=filters.photo | filters.document,
                timeout=60,
            )
            path = os.path.join(EXTRAS_DIR, f"{chat_id}_watermark.png")
            await client.download_media(asked, file_name=path)
            set_watermark_image(chat_id, path)
            toggle_watermark(chat_id, True)
            await asked.reply_text(
                "✅ Image watermark set ho gaya aur ON kar diya gaya hai!\n\n"
                "/videosettings se OFF/ON control karo."
            )
    except ListenerTimeout:
        await client.send_message(chat_id, "⚠️ Time out ho gaya. /setwatermark se dobara try karo.")


@Client.on_message(filters.private & filters.command("removewatermark"))
async def remove_watermark_cmd(client, message: Message):
    ex = get_extras(message.chat.id)
    if ex["watermark_image"] and os.path.exists(ex["watermark_image"]):
        try:
            os.remove(ex["watermark_image"])
        except Exception:
            pass
    del_watermark(message.chat.id)
    await message.reply_text("🗑️ Watermark remove kar diya gaya.")




# @kingbots — Intro / Outro / Watermark feature
