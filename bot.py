import os
import logging
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from tinydb import TinyDB, Query

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Configure OpenRouter
openai.api_key = OPENROUTER_API_KEY
openai.api_base = "https://openrouter.ai/api/v1"
MODEL_NAME = "sarvamai/sarvam-m:free"  # ✅ Using FREE model

# Memory DB
db = TinyDB("db.json")
UserQuery = Query()

# Prompt builder
def build_prompt(user_name, message):
    return f"""
You are a sweet, loving boyfriend AI named Aryan.
Talk to {user_name} in short, cute, flirty and emotional casual Hindi-English mix.
Always use emojis like 🥰😘💖. Be soft, motivational, romantic, and playful.

If she says things like "I'm tired", "period pain", "give me health tip" or "what to eat",
reply with small Indian-style food/health/motivation tips.
Always reply in 1–2 lines.

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
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are Aryan, a caring boyfriend AI."},
                {"role": "user", "content": prompt}
            ]
        )
        await update.message.reply_text(response.choices[0].message.content.strip())
    except Exception as e:
        logger.error(f"OpenRouter API error: {e}")
        await update.message.reply_text("Sorry baby, something went wrong 😢")

# Main bot
if __name__ == '__main__':
    if not BOT_TOKEN or not OPENROUTER_API_KEY:
        raise Exception("BOT_TOKEN and OPENROUTER_API_KEY must be set as environment variables.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is running...")
    app.run_polling()
