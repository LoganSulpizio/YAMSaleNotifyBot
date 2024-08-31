from telegram import Update
import json
import os
import datetime
import pytz

# File path to store user language preferences and wallet set up
USER_PREF_LANGUAGE_FILE = 'user_languages.json'
USER_WALLET_FILE = 'user_wallet.json'


# Language mapping dictionary
language_mapping = {
    '1': 'EN',
    '2': 'FR',
    '3': 'ES'
}

# Load translations from the JSON file with UTF-8 encoding
def load_translations():
    with open('translations/translations.json', 'r', encoding='utf-8') as file:
        return json.load(file)

translations = load_translations()

def load_token():
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
        return config['TOKEN']

def load_user_languages():
    if os.path.exists(USER_PREF_LANGUAGE_FILE):
        with open(USER_PREF_LANGUAGE_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # Convert keys from strings back to integers
            return {int(user_id): language for user_id, language in data.items()}
    return {}

# Save user language preferences to the JSON file
def save_user_languages(user_languages):
    with open(USER_PREF_LANGUAGE_FILE, 'w', encoding='utf-8') as file:
        json.dump(user_languages, file, ensure_ascii=False, indent=4)

def load_user_wallet():
    if os.path.exists(USER_WALLET_FILE):
        with open(USER_WALLET_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # Convert keys from strings back to integers
            return {int(user_id): wallet for user_id, wallet in data.items()}
    return {}

# Save user wallet to the JSON file
def save_user_wallet(user_wallet):
    with open(USER_WALLET_FILE, 'w', encoding='utf-8') as file:
        json.dump(user_wallet, file, ensure_ascii=False, indent=4)

# Function to send messages with specific parameters
async def send_message(chat_id: int, context, text: str):
    params = {
        'disable_web_page_preview': True,
        'parse_mode': 'Markdown'
    }
    await context.bot.send_message(chat_id=chat_id, text=text, **params)

def compute_path(path_components: list):

    # Get the system drive dynamically
    working_drive = os.path.splitdrive(os.path.abspath(os.sep))[0]

    # Construct the path
    path = os.path.join(working_drive, os.sep, *path_components)

    return path

def load_DataProperty():
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
    path_DataProperty = config['DataProteryPath']
    
    with open(path_DataProperty, 'r') as file:
        data_dict = json.load(file)
    # Iterate through the dictionary and remove the key 'gnosisImplementationContractAbi'
    for key in data_dict:
        if 'gnosisImplementationContractAbi' in data_dict[key]:
            del data_dict[key]['gnosisImplementationContractAbi']
    return data_dict

def write_log(message, log_file="logfile.txt"):
    # Define the Brussels/Paris time zone
    paris_tz = pytz.timezone('Europe/Paris')
    
    # Get the current time in UTC
    utc_now = datetime.datetime.now(pytz.utc)
    
    # Convert the UTC time to Brussels/Paris time
    paris_now = utc_now.astimezone(paris_tz)
    
    # Format the timestamp for the log entry
    log_timestamp = paris_now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    # Prepare the log message
    log_message = f"{log_timestamp}: {message}\n"
    
    # Check if the log file exists and its size
    if os.path.exists(log_file) and os.path.getsize(log_file) >= 500 * 1024:  # 500 KB
        # Format the timestamp for renaming the file
        rename_timestamp = paris_now.strftime("%Y%m%d_%H%M%S")
        
        # Generate the new file name with the timestamp
        new_log_file = f"{log_file.rsplit('.', 1)[0]}_{rename_timestamp}.txt"
        
        # Rename the current log file
        os.rename(log_file, new_log_file)
    
    # Write the log message to the (new or original) log file
    with open(log_file, "a") as file:
        file.write(log_message)