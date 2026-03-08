from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
import random
import os

TOKEN = os.environ.get("BOT_TOKEN")  # Railway Secrets orqali qo'yiladi

# /start buyrug'i
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot ishga tushdi ✅")

# Welcome + Captcha
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        captcha = str(random.randint(1000, 9999))
        context.user_data[user.id] = captcha

        keyboard = InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(f"Verify {captcha}", callback_data=f"verify:{captcha}:{user.id}")
        )

        await update.message.reply_text(
            f"Xush kelibsiz {user.first_name}! Captcha tugmasini bosing.",
            reply_markup=keyboard
        )
        try:
            await update.message.delete()
        except:
            pass

# Captcha callback
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("verify:"):
        captcha, user_id = data.split(":")[1], int(data.split(":")[2])
        if context.user_data.get(user_id) == captcha:
            await query.edit_message_text("✅ Tasdiqlandi!")
            context.user_data.pop(user_id)
        else:
            await query.edit_message_text("❌ Noto'g'ri captcha!")

# Join/leave xabarlarni o'chirish
async def delete_service_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.delete()
    except:
        pass

# Spam va link filter
async def block_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    if "http" in text or "t.me" in text:
        try:
            await update.message.delete()
        except:
            pass

# Application
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS | filters.StatusUpdate.LEFT_CHAT_MEMBER, delete_service_messages))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, block_links))
app.add_handler(CallbackQueryHandler(button_callback))

app.run_polling()