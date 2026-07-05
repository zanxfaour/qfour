from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from pyrogram import Client
import asyncio

TOKEN = "8956980779:AAHRTwK24zV0VvMhisfX26vWfKp8p6bBrJ4"
API_ID = 34652513
API_HASH = "cae6e7baddc07d439c0b227a650a0634"
CHANNEL = "Q4men"

async def fetch_posts(section):
    posts = []
    async with Client("session", api_id=API_ID, api_hash=API_HASH) as app:
        async for message in app.get_chat_history(CHANNEL, limit=100):
            text = message.caption or message.text or ""
            if f"القسم: {section}" in text:
                posts.append({
                    "id": message.id,
                    "text": text,
                    "photo": message.photo.file_id if message.photo else None
                })
    return posts

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👕 علوي", callback_data="علوي")],
        [InlineKeyboardButton("👖 سفلي", callback_data="سفلي")],
        [InlineKeyboardButton("👔 طقم", callback_data="طقم")],
    ]
    await update.message.reply_text(
        "اختر القسم:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    section = query.data

    await query.edit_message_text(f"⏳ جاري تحميل منتجات {section}...")

    posts = await fetch_posts(section)

    if not posts:
        await query.edit_message_text(
            f"ما في منتجات في قسم {section} حالياً.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
            ])
        )
        return

    for post in posts:
        link = f"https://t.me/{CHANNEL}/{post['id']}"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 شاهد المنتج", url=link)]
        ])
        if post["photo"]:
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=post["photo"],
                caption=post["text"],
                reply_markup=keyboard
            )
        else:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=post["text"],
                reply_markup=keyboard
            )

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"✅ انتهت منتجات {section}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 رجوع للأقسام", callback_data="back")]
        ])
    )

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("👕 علوي", callback_data="علوي")],
        [InlineKeyboardButton("👖 سفلي", callback_data="سفلي")],
        [InlineKeyboardButton("👔 طقم", callback_data="طقم")],
    ]
    await query.edit_message_text(
        "اختر القسم:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(back, pattern="^back$"))
app.add_handler(CallbackQueryHandler(button))
app.run_polling()
