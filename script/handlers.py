from telegram import Update
from telegram.ext import ContextTypes
from language_handlers import translate

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f'[EN] Welcome - use /setlanguage to select your language\n' +
        f'[FR] Bienvenue - utilisez /setlanguage pour sélectionner votre langue'
    )

# You can add more command handlers here as you expand your bot's functionality