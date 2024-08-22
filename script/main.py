from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters
from utilities import load_token, load_user_languages
from language_handlers import setlanguage, handle_language_selection, cancel, LANGUAGE_SELECTION, initialize_user_languages
from handlers import start

def main():
    token = load_token()

    application = ApplicationBuilder().token(token).build()

    # Load user language preferences and initialize in the language_handlers module
    user_languages = load_user_languages()
    initialize_user_languages(user_languages)

    # Register the /start command handler
    application.add_handler(CommandHandler("start", start))
    
    # Register the conversation handler for /setlanguage
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('setlanguage', setlanguage)],
        states={
            LANGUAGE_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_language_selection)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    application.add_handler(conv_handler)

    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()