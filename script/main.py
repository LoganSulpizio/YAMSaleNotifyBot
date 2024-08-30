from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler, JobQueue
from utilities import load_token, load_user_languages, load_user_wallet, load_DataProperty, compute_path
from language_handlers import setlanguage, handle_language_selection, cancel, LANGUAGE_SELECTION, initialize_user_languages
from handlers import start, about, setwallet, handle_wallet_input, checkinfo, WALLET_INPUT, initialize_user_wallet
from process_tx_file import check_for_new_sales_event
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

# Suppress PTBUserWarning related to CallbackQueryHandler
filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

def main():
    token = load_token()
    DataProperty = load_DataProperty()

    application = ApplicationBuilder().token(token).build()

    # Ensure JobQueue is initialized
    job_queue = application.job_queue

    # Load user language preferences and initialize in the language_handlers module
    user_languages = load_user_languages()
    initialize_user_languages(user_languages)

    # Load user wallet and initialize in the handlers module
    user_wallets = load_user_wallet()
    initialize_user_wallet(user_wallets)

    # Register the conversation handler for /setlanguage and /start
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('setlanguage', setlanguage),
            CommandHandler('start', start)  # Start also triggers language selection
        ],
        states={
            LANGUAGE_SELECTION: [CallbackQueryHandler(handle_language_selection)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_user=True,    # Ensures each user has their own conversation
        per_chat=True     # Ensures each chat has its own conversation context
    )
    application.add_handler(conv_handler)

    # Register the /about command handler
    application.add_handler(CommandHandler("about", about))
    
    # Register the /checkinfo command handler
    application.add_handler(CommandHandler("checkinfo", checkinfo))

    # Register the conversation handler for /setwallet
    wallet_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('setwallet', setwallet)],
        states={
            WALLET_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wallet_input)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_user=True,    # Ensures each user has their own conversation
        per_chat=True     # Ensures each chat has its own conversation context
    )
    application.add_handler(wallet_conv_handler)

    # Schedule the job to run every 10 seconds
    job_queue.run_repeating(
        check_for_new_sales_event,
        interval=10,
        first=10,  # first run after 10 seconds
        data={
            'user_wallets': user_wallets,  # Passes user_wallets to the job's context
            'DataProperty': DataProperty,  # Passes DataProperty to the job's context
            'path_transaction_queue_folder': 'transactions_queue/'  # Passes the folder path to the job's context
        }
    )

    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()