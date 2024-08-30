from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from utilities import translations, language_mapping, save_user_languages, send_message

# Conversation states
LANGUAGE_SELECTION = 1

# Dictionary to store user language preferences (loaded from file)
user_languages = {}

def initialize_user_languages(loaded_languages):
    global user_languages
    user_languages = loaded_languages

# Getter for user_languages
def get_user_languages():
    return user_languages

# Function to get the correct translation for the user's language with fallback to English
def translate(user_id, key, **kwargs):
    # Get the user's selected language or default to English
    language = user_languages.get(user_id, 'EN')
    
    # Try to get the translation in the user's language
    translation = translations.get(language, {}).get(key)
    
    if translation is None:
        # If not found, fallback to English
        translation = translations['EN'].get(key, '')

    # Return the translation with formatted values if any are provided
    return translation.format(**kwargs)

async def setlanguage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id

    # Inline keyboard buttons for language selection
    keyboard = [
        [InlineKeyboardButton("English", callback_data='1')],
        [InlineKeyboardButton("Français", callback_data='2')],
        [InlineKeyboardButton("Español", callback_data='3')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    select_language_message = translate(user_id, 'select_language_prompt')
    
    # Send the message with the inline keyboard attached
    await update.message.reply_text(select_language_message, reply_markup=reply_markup)
    
    return LANGUAGE_SELECTION  # Move to LANGUAGE_SELECTION state

async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    user_id = query.from_user.id
    text = query.data  # Get the data from the callback

    if text in language_mapping:
        user_languages[user_id] = language_mapping[text]
        save_user_languages(user_languages)  # Save the updated preferences
        language_set_message = translate(user_id, 'language_set')
        await query.answer()  # Acknowledge the callback
        await send_message(update, context, language_set_message)
        return ConversationHandler.END  # End the conversation
    else:
        invalid_selection_message = translate(user_id, 'invalid_selection')
        await send_message(update, context, invalid_selection_message)
        return LANGUAGE_SELECTION  # Stay in the same state

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await send_message(update, context, "Operation cancelled.")
    return ConversationHandler.END  # End the conversation
