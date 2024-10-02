from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from telegram.error import NetworkError, TelegramError
from utilities import load_token, load_user_languages, load_user_wallet, load_DataProperty, reload_DataProperty, write_log, send_telegram_alert
from language_handlers import setlanguage, handle_language_selection, cancel, LANGUAGE_SELECTION, initialize_user_languages, reinitialize_user_commands
from handlers import start, about, setwallet, handle_wallet_input, checkinfo, WALLET_INPUT, initialize_user_wallet
from process_tx_file import check_for_new_sales_event
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning
import time
from datetime import time as time_obj

# Suppress PTBUserWarning related to CallbackQueryHandler
filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

def main():
    try:
        token = load_token()
        DataProperty = load_DataProperty()

        application = ApplicationBuilder().token(token).build()

        # Ensure JobQueue is initialized
        job_queue = application.job_queue

        # Load user language preferences and initialize in the language_handlers module
        user_languages = load_user_languages()
        initialize_user_languages(user_languages)
        # initialize the custom commands according to each user's preferred language
        reinitialize_user_commands(application)
        print("Custom commands according to each user's preferred language have been set")
        write_log("Custom commands according to each user's preferred language have been set", "logfile/logfile_YAMSaleNotifyBot.txt")

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

        # Schedule the job to run every 8 seconds
        job_queue.run_repeating(
            check_for_new_sales_event,
            interval=8,
            first=8,  # first run after 8 seconds
            data={
                'user_wallets': user_wallets,  # Passes user_wallets to the job's context
                'DataProperty': DataProperty,  # Passes DataProperty to the job's context
                'path_transaction_queue_folder': 'transactions_queue/'  # Passes the folder path to the job's context
            }
        )

        # Schedule daily update of DataProperty at 7 AM
        job_queue.run_daily(
            reload_DataProperty,
            time=time_obj(3, 0),  # Schedule for 5:00 AM (time in utc)
            data={'DataProperty': DataProperty}
        )

        # Run the bot
        print("YAMSaleNotifyBot running...")
        write_log("YAMSaleNotifyBot running...", "logfile/logfile_YAMSaleNotifyBot.txt")

        while True:
            try:
                application.run_polling()
            except NetworkError:
                print("NetworkError: Retrying in 5 seconds...")
                write_log("NetworkError: Retrying in 5 seconds...", "logfile/logfile_YAMSaleNotifyBot.txt")
                time.sleep(5)
            except TelegramError as e:
                print(f"TelegramError occurred: {str(e)}")
                write_log(f"TelegramError occurred: {str(e)}", "logfile/logfile_YAMSaleNotifyBot.txt")
                send_telegram_alert(f"YAMSaleNotifyBot - TelegramError occurred: {str(e)}")
                time.sleep(5)
            except Exception as e:
                # Log the error using write_log
                write_log(f"An error occured: {str(e)}", "logfile/logfile_YAMSaleNotifyBot.txt")
                send_telegram_alert(f"YAMSaleNotifyBot - An error occurred: {str(e)}")
            

    except Exception as e:
        # Log the error using write_log
        write_log(f"An error occured: {str(e)}", "logfile/logfile_YAMSaleNotifyBot.txt")
        send_telegram_alert(f"YAMSaleNotifyBot - An error occurred: {str(e)}")

if __name__ == '__main__':
    try:
        write_log("script started", "logfile/logfile_YAMSaleNotifyBot.txt")
        print('script started')
        main()
    except Exception as e:
        write_log(f"Critical error in main: {str(e)}", "logfile/logfile_YAMSaleNotifyBot.txt")
