import sqlite3
from typing import List

def get_all_offer_ids_by_seller(db_path: str, seller_address: str, status: List[str] = ['InProgress', 'SoldOut', 'Deleted']) -> List[int]:
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Prepare the SQL query with placeholders for the status list
    query = f"SELECT offer_id FROM offers WHERE seller_address = ? AND status IN ({','.join('?' for _ in status)})"
    
    # Execute the query with seller_address and the status list as parameters
    cursor.execute(query, (seller_address, *status))
    offer_ids = cursor.fetchall()

    # Extract the offer_id from each row and store in a list
    offer_id_list = [row[0] for row in offer_ids]

    # Close the connection
    conn.close()

    return offer_id_list
