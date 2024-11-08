import json
import os
import datetime
import pytz
import requests
from web3 import Web3

# File path to store user language preferences and wallet set up
USER_PREF_LANGUAGE_FILE = 'user_languages.json'
USER_WALLET_FILE = 'user_wallet.json'


# Language mapping dictionary
language_mapping = {
    '1': 'EN',
    '2': 'FR',
    '3': 'ES'
}

def write_log(message, log_file="logfile/logfile.txt"):
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
    
    if utc_now.hour % 4 == 0 and utc_now.minute % 4 == 0:

        # Check if the log file exists and its size
        if os.path.exists(log_file) and os.path.getsize(log_file) >= 3000 * 1024:  # 3000 KB
            # Format the timestamp for renaming the file
            rename_timestamp = paris_now.strftime("%Y%m%d_%H%M%S")
            
            # Generate the new file name with the timestamp
            new_log_file = f"{log_file.rsplit('.', 1)[0]}_{rename_timestamp}.txt"
            
            # Rename the current log file
            os.rename(log_file, new_log_file)
    
    # Write the log message to the (new or original) log file
    with open(log_file, "a") as file:
        file.write(log_message)


# Load translations from the JSON file with UTF-8 encoding
def load_translations():
    with open('translations/translations.json', 'r', encoding='utf-8') as file:
        return json.load(file)

translations = load_translations()

def load_token():
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
        return config['TOKEN']

def load_db_path():
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
        return config['db_path']

def load_w3():
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
        return Web3(Web3.HTTPProvider(config['w3_url_1']))

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
    write_log("DataProperty loaded successfully", "logfile/logfile_YAMSaleNotifyBot.txt")
    return data_dict

async def reload_DataProperty(context):
    try:
        new_data_property = load_DataProperty()
        
        # Update the DataProperty in the job's context
        context.job.data['DataProperty'].update(new_data_property)

    except Exception as e:
        # Log any failure during the update
        write_log(f"Failed to reload DataProperty: {str(e)}", "logfile/logfile_YAMSaleNotifyBot.txt")


def send_telegram_alert(message):

    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
        group_id = config["chat_id_alert"]
        bot_token = config["bot_alert_token"]

    # The Telegram Bot API endpoint URL
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    
    # Parameters for the message
    params = {
        'chat_id': group_id,
        'text': message,
        'disable_web_page_preview': True,
        'parse_mode': 'Markdown'
    }
    
    # Send the message
    response = requests.post(url, json=params)

    return response
