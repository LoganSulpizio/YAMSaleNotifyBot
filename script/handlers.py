from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from eth_utils import is_address, to_checksum_address
from language_handlers import translate, get_user_languages, setlanguage
from utilities import send_message, save_user_wallet

# Conversation states
WALLET_INPUT = 2

# Dictionaries to store user data (initialized from file)
user_wallets = {}

def initialize_user_wallet(loaded_wallets):
    global user_wallets
    user_wallets = loaded_wallets


# Function to handle the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        f'[EN] *Welcome!*\n' +
        f'[FR] *Bienvenue!*\n' + 
        f'[ES] *¡Bienvenido!*'
        )
    # Call the setlanguage function to start the language selection process
    return await setlanguage(update, context)

# Function to handle the /about command
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    about_message = translate(user_id, 'about') + "[Github](https://github.com/LoganSulpizio/YAMSaleNotifyBot)"
    await send_message(update, context, about_message)

# Function to handle the /setwallet command
async def setwallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    wallet_prompt_message = translate(user_id, 'set_your_wallet')
    await send_message(update, context, wallet_prompt_message)
    return WALLET_INPUT  # Move to WALLET_INPUT state

# Function to handle wallet input
async def handle_wallet_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    wallet_address = update.message.text.strip()

    # Check if the wallet address is valid
    if is_address(wallet_address):
        # Convert to checksummed address
        checksummed_address = to_checksum_address(wallet_address)
        
        # Store the checksummed wallet address in the dictionary
        user_wallets[user_id] = checksummed_address
        save_user_wallet(user_wallets)

        wallet_set_message = translate(user_id, 'wallet_has_been_set')
        await send_message(update, context, wallet_set_message)
    else:
        # If the address is invalid, send an error message
        invalid_wallet_message = translate(user_id, 'invalid_wallet_format')
        await send_message(update, context, invalid_wallet_message)

    return ConversationHandler.END  # End the conversation

# Function to handle the /checkinfo command
async def checkinfo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    # Retrieve user's language and wallet information
    user_languages = get_user_languages()
    user_language = user_languages.get(user_id, None)
    user_wallet = user_wallets.get(user_id, None)

    if user_language is not None:
        language_message = translate(user_id, 'check_language', user_language=user_language) + '\n'
    else:
        language_message = translate(user_id, 'check_language_none') + '\n'
    
    if user_wallet is not None:
        wallet_message = translate(user_id, 'check_wallet', user_wallet=user_wallet)
    else:
        wallet_message = translate(user_id, 'check_wallet_none')

    await send_message(update, context, language_message + wallet_message)

# You can add more command handlers here as you expand your bot's functionality
