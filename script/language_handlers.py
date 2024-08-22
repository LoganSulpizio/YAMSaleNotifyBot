from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from utilities import translations, language_mapping, save_user_languages

# Conversation states
LANGUAGE_SELECTION = 1

# Dictionary to store user language preferences (loaded from file)
user_languages = {}

def initialize_user_languages(loaded_languages):
    global user_languages
    user_languages = loaded_languages

# Function to get the correct translation for the user's language
def translate(user_id, key):
    language = user_languages.get(user_id, 'EN')
    return translations[language].get(key, '')

async def setlanguage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    select_language_message = translate(user_id, 'select_language_prompt') + '\n1 = English\n2 = Français'
    await update.message.reply_text(select_language_message)
    return LANGUAGE_SELECTION  # Move to LANGUAGE_SELECTION state

async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if text in language_mapping:
        user_languages[user_id] = language_mapping[text]
        save_user_languages(user_languages)  # Save the updated preferences
        language_set_message = translate(user_id, 'language_set')
        await update.message.reply_text(language_set_message)
        return ConversationHandler.END  # End the conversation
    else:
        invalid_selection_message = translate(user_id, 'invalid_selection')
        await update.message.reply_text(invalid_selection_message)
        return LANGUAGE_SELECTION  # Stay in the same state

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END  # End the conversation