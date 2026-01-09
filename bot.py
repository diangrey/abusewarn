import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 1999645649
BADWORDS_FILE = "badwords.txt"


def load_badwords():
    if not os.path.exists(BADWORDS_FILE):
        return []
    with open(BADWORDS_FILE, "r", encoding="utf-8") as f:
        return [x.strip().lower() for x in f.readlines() if x.strip()]


def save_badword(word):
    with open(BADWORDS_FILE, "a", encoding="utf-8") as f:
        f.write(word + "\n")


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if chat.type == "private":
        await update.message.reply_text(
            "👋 Hello!\n\n"
            "🛡️ I am an Abuse Control Bot.\n"
            "• Make me admin (Delete Messages permission)\n"
            "I automatically delete abusive messages in Telegram groups."
        )
    else:
        await update.message.reply_text(
            "✅ Abuse Control Bot is active!\n"
            "⚠️ Abusive language will be deleted automatically."
        )


# /add command (owner only)
async def add_badword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:
        await update.message.reply_text("Usage: /add word")
        return

    word = context.args[0].lower()
    badwords = load_badwords()

    if word in badwords:
        await update.message.reply_text("❌ Word already exists")
        return

    save_badword(word)
    await update.message.reply_text(f"✅ Abusive word added: {word}")


# message checker (groups only)
async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        return

    text = update.message.text.lower()
    badwords = load_badwords()

    for word in badwords:
        if word in text:
            try:
                await update.message.delete()
                await context.bot.send_message(
                    chat_id=chat.id,
                    text="⚠️ Abusive language is not allowed here!"
                )
            except:
                pass
            break


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_badword))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
