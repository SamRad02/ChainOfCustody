import argparse
import os
from blockchain import Blockchain
from utils import get_role_passwords
from datetime import datetime

def parse_items_args(args):
    parser = argparse.ArgumentParser(description='Show evidence items for a case')
    parser.add_argument('-c', '--case_id', required=True, help='Case identifier')
    parser.add_argument('-p', '--password', required=True, help='Password for authentication')
    return parser.parse_args(args)

def format_timestamp(timestamp):
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def show_case_items(case_id, password):
    blockchain_file = os.getenv('BCHOC_FILE_PATH', 'blockchain.bin')
    
    if not os.path.exists(blockchain_file):
        print("Error: blockchain file not found")
        exit(1)
    
    try:
        blockchain = Blockchain(blockchain_file)
        
        # Track the latest state of each evidence item
        evidence_items = {}  # Dictionary to store latest state of each item
        
        # Process all blocks
        for block in blockchain.blocks:
            # Skip genesis block
            if block.state == b"INITIAL\0\0\0\0\0":
                continue
                
            # Decrypt block values
            decrypted_values = block.get_decrypted_values(password)
            
            # Check if this block belongs to our case
            if decrypted_values['case_id'] == case_id:
                evidence_id = decrypted_values['evidence_id']
                state = block.state.rstrip(b'\0').decode()
                
                # Update or add evidence item
                evidence_items[evidence_id] = {
                    'state': state,
                    'timestamp': block.timestamp
                }
        
        # Print results
        if evidence_items:
            for evidence_id, info in sorted(evidence_items.items()):
                print(f"Item: {evidence_id}")
                print(f"State: {info['state']}")
                print(f"Time of action: {format_timestamp(info['timestamp'])}")
                print()  # Empty line between items
        else:
            print(f"No items found for case: {case_id}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

def run():
    import sys
    args = parse_items_args(sys.argv[2:])  # Skip the first two arguments (script name and command)
    show_case_items(args.case_id, args.password)

if __name__ == "__main__":
    run()