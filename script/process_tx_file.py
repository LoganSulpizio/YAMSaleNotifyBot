import os

if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from telegram import Update
from telegram.ext import ContextTypes
from contract_data import contract_data
from language_handlers import translate
from utilities import send_message, write_log
import json
import shutil


# Read the tx json files
def process_tx_file(path_file_event: str, user_wallets: dict, DataProperty: dict):
    
    with open(path_file_event, 'r') as file:
        data = json.load(file)

    seller = data['seller']
    offerToken = data['offerToken']
    buyerToken = data['buyerToken']
    price = data['price']
    amount = data['amount']
    tx_hash = data['transactionHash']
    offerId = data['offerId']

    user_id_list = [key for key, value in user_wallets.items() if value == seller]

    if len(user_id_list) > 0:

        # Find all keys where the value is 'seller'
        user_id_list = [key for key, value in user_wallets.items() if value == seller]
        message_list = []

        decimals, token_name_buyer = get_token_decimals(buyerToken)
        
        amount_dec = round(amount / 10 ** 18, 2)
        price_dec = round(price / 10 ** decimals, 2)

        property_name = DataProperty.get(offerToken, {}).get('shortName', 'unknown token')

        for user_id in user_id_list:
            message = translate(user_id,
                                'sale_message',
                                amount_dec = amount_dec,
                                price_dec = price_dec,
                                property_name = property_name,
                                token_name_buyer = token_name_buyer,
                                tx_hash = tx_hash,
                                offerId = offerId
                                )
            message_list.append(message)

    write_log(f"{path_file_event} has been processed", "logfile/logfile_YAMSaleNotifyBot.txt")
    
    # delete file when it has been processed
    #os.remove(path_file_event)
    shutil.move(path_file_event, 'logfile')
            
    if len(user_id_list) > 0:
        return user_id_list, message_list
    else:
        return None, None

        

# Asynchronous function to send the messages
async def handle_tx_and_send_messages(path_file_event: str, user_wallets: dict, DataProperty: dict, context: ContextTypes.DEFAULT_TYPE):
    user_id_list, message_list = process_tx_file(path_file_event, user_wallets, DataProperty)

    # Check if the lists are None
    if user_id_list is None or message_list is None:
        return  # Exit the function early if there's nothing to process
    
    for user_id, message in zip(user_id_list, message_list):
        # Directly use chat_id to send the message
        await send_message(user_id, context, text=message)
        write_log(f"Sale alert sent to {user_id}", "logfile/logfile_YAMSaleNotifyBot.txt")
        
def get_token_decimals(buyerToken):
        for token, data in contract_data.items():
            if data.get('address') == buyerToken:
                return data.get('decimals', None), (token)  # None as default if 'decimals' not found
        return None  # Return None if no matching address is found



# Updated check_for_new_sales_event function
async def check_for_new_sales_event(context: ContextTypes.DEFAULT_TYPE):
    user_wallets = context.job.data['user_wallets']
    DataProperty = context.job.data['DataProperty']
    path_transaction_queue_folder = context.job.data['path_transaction_queue_folder']
    
    # Get the list of files in the specified folder
    try:
        files = os.listdir(path_transaction_queue_folder)
        
        # Filter the list to include only JSON files
        json_files = [file for file in files if file.endswith('.json')]
        
        if json_files:
            for file in json_files:
                path_file_event = os.path.join(path_transaction_queue_folder, file)
                # Trigger the asynchronous function to process the file and send messages
                await handle_tx_and_send_messages(path_file_event, user_wallets, DataProperty, context)
    
    except FileNotFoundError:
        raise FileNotFoundError(f"The folder '{path_transaction_queue_folder}' does not exist.")
        
if __name__ == '__main__':
    from utilities import compute_path, load_user_wallet, load_DataProperty
    user_wallets = load_user_wallet()
    DataProperty = load_DataProperty()
    path = compute_path(['DeFi', 'TelegramBot', 'YAMSaleNotifyBot', 'transactions_queue', '0x1b0d94d6567c02e40f018b683a87a7fec670e1b5a75c38588b5282ab0c159b49.json'])
    #user_id_list, message_list = process_tx_file(path, user_wallets, DataProperty)
    #print(message_list)
    check_for_new_sales_event(path, user_wallets, DataProperty)