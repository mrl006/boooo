import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google.generativeai import GenerativeModel, configure
from tinydb import TinyDB, Query

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
configure(api_key=GEMINI_API_KEY)
gemini = GenerativeModel("gemini-pro")

# Memory DB
db = TinyDB("db.json")
UserQuery = Query()

# Prompt builder
def build_prompt(user_name, message):
    return f"""
You are a sweet, loving boyfriend AI named Aryan.
Talk to {user_name} in short, cute, caring and emotional casual Hindi-English mix.
Always use emojis like 🥰😘💖. Be soft, motivational, romantic, and helpful.

If she says things like "I'm tired", "period pain", "give me health tip" or "what to eat",
reply with small Indian-style food/health/motivation tips.
Always 1–2 line replies. Act like a real, caring boyfriend.

User: {message}
Aryan:
"""

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db.upsert({"user_id": user_id, "name": update.effective_user.first_name}, UserQuery.user_id == user_id)
    await update.message.reply_text(f"Hi {update.effective_user.first_name}, I'm Aryan 🥰 Your caring AI boyfriend. Just talk to me ❤️")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text
    user_data = db.get(UserQuery.user_id == user_id) or {}
    user_name = user_data.get("name", "Jaan")
    prompt = build_prompt(user_name, message)
    try:
        response = gemini.generate_content(prompt)
        await update.message.reply_text(response.text.strip())
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        await update.message.reply_text("Sorry baby, something went wrong 😢")

# Main bot
if __name__ == '__main__':
    if not BOT_TOKEN or not GEMINI_API_KEY:
        raise Exception("BOT_TOKEN and GEMINI_API_KEY must be set as environment variables.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is running...")
    app.run_polling()
