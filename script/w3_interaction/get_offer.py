import sys
import os
if __name__ == '__main__':
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from web3 import Web3
from web3.exceptions import Web3RPCError
from typing import List, Optional, Any
from contract_data import contract_data
from utilities import send_message, save_user_wallet, write_log


async def get_offer(w3: Web3, offer_id: int) -> Optional[List]:
    """
    Fetch an offer based on its ID from the YAM contract.
    The call on the YAM contract is 'showOffer'

    Args:
        w3 (Web3): An instance of the Web3 connection.
        offer_id (int): The ID of the offer to retrieve.

    Returns:
        Optional[List]: The offer data as a list if successful, None if not found or invalid.
    """
    # Instantiate the token contract
    token_contract = w3.eth.contract(address=contract_data['YAM']['address'], abi=contract_data['YAM']['abi'])

    try:
        # Redirect stderr to suppress the error message (Web3RPCError prints at the console an error when there is an Web3RPCError. I didn't manage removing it "nicely" so I do't it the hard way...)
        with open(os.devnull, 'w') as devnull:
            old_stderr = sys.stderr
            sys.stderr = devnull
            try:
                # Call the showOffer function
                offer = token_contract.functions.showOffer(offer_id).call()
                return offer
            finally:
                # Restore stderr
                sys.stderr = old_stderr

    except (ValueError, Web3RPCError) as e:
        write_log(f"Exception in get_offer for offer id {offer_id}: {e}", "logfile/logfile_YAMSaleNotifyBot.txt")
        return None

async def get_multiple_offers(w3: Web3, offer_ids: List[int]) -> List[Optional[List]]:
    """
    Fetch multiple offers concurrently based on their IDs.

    Args:
        w3 (Web3): An instance of the Web3 connection.
        offer_ids (List[int]): A list of offer IDs to retrieve.

    Returns:
        List[Optional[List]]: A list of multiples items.
                              Each item is the list returned by the call 'showOffer' where the offer id was added at the end of the list 
                              Each entry will be None if the corresponding offer is not found or invalid.
    """
    tasks = []
    for offer_id in offer_ids:
        tasks.append(get_offer(w3, offer_id))  # Create a task for each offer ID

    # Await all tasks concurrently and collect results
    results = await asyncio.gather(*tasks)
    
    # Append offer_id to each result
    final_results = []
    for offer_id, offer in zip(offer_ids, results):
        if offer is not None:
            final_results.append(offer + [offer_id])  # Append offer data and offer_id
        else:
            final_results.append([None, offer_id])  # Keep track of the offer_id even if not found
    
    write_log(f"{len(final_results)} offers retrieved from w3 rpc", "logfile/logfile_YAMSaleNotifyBot.txt")

    return final_results

### test case ###
if __name__ == '__main__':

    import json
    from web3 import Web3
    from web3.exceptions import Web3RPCError
    from YAM_DB_handlers.get_all_offer_ids_by_seller import get_all_offer_ids_by_seller
    from pprint import pprint
    
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
        db_path = config["db_path"]
        w3_url = config["w3_url_1"]
    
    w3 = Web3(Web3.HTTPProvider(w3_url))

    offer_ids = get_all_offer_ids_by_seller(db_path, "0xA99e07efB152321117653a16727BF6Bc02106892", ['InProgress'])
    print('ready')
    # Run the get_multiple_offers function
    results = asyncio.run(get_multiple_offers(w3, offer_ids))
    
    pprint(results)
