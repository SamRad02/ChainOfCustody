import os
import sys
import argparse
from datetime import datetime
from blockchain import Blockchain
from utils import validate_password, get_role_passwords, get_owner

def parse_summary_args(args):
    parser = argparse.ArgumentParser(description='Show summary of evidence items')
    parser.add_argument('-c', '--case_id', required=True, help='Case identifier (UUID)')
    return parser.parse_args(args)

def countItems(case_id):
    # Get blockchain file path from environment variable
    blockchain_file = os.getenv('BCHOC_FILE_PATH', 'blockchain.bin')
    
    # Check if blockchain file exists
    if not os.path.exists(blockchain_file):
        print("Error: blockchain file not found")
        exit(1)

    # Load the blockchain
    blockchain = Blockchain(blockchain_file)
    itemsList = []

    creator_password = get_role_passwords()['creator']

    uniqueCount = 0
    checkedIn = 0
    checkedOut = 0
    disposed = 0
    destroyed = 0
    released = 0

    for block in blockchain.blocks:
        # ignore genesis block
        if block.state == b"INITIAL\0\0\0\0\0":
            continue
        
        # decrypt the blocks
        decrypted_values = block.get_decrypted_values(creator_password)

        # add case ID's to list if it is unique
        if decrypted_values['case_id'] == case_id and decrypted_values['evidence_id'] not in itemsList:
            itemsList.append(decrypted_values['evidence_id'])
            uniqueCount = uniqueCount + 1

        # Check if item is checked in
        if block.state.rstrip(b'\0') == b"CHECKEDIN":
            checkedIn = checkedIn + 1

        # Check is item is checked out
        if block.state.rstrip(b'\0') == b"CHECKEDOUT":
            checkedOut = checkedOut + 1

        # Check is item is disposed
        if block.state.rstrip(b'\0') == b"DISPOSED":
            disposed = disposed + 1

        # Check is item is destroyed
        if block.state.rstrip(b'\0') == b"DESTROYED":
            destroyed = destroyed + 1    

        # Check is item is released
        if block.state.rstrip(b'\0') == b"RELEASED":
            released = released + 1  

    return uniqueCount, checkedIn, checkedOut, disposed, destroyed, released

def run():
    args = parse_summary_args(sys.argv[2:])
    uniqueCount, checkedIn, checkedOut, disposed, destroyed, released = countItems(args.case_id)

    # Print output in the expected format
    print(f"Case Summary for Case ID: {args.case_id}")
    print(f"Total Evidence Items: {uniqueCount}")
    print(f"Checked In: {checkedIn}")
    print(f"Checked Out: {checkedOut}")
    print(f"Disposed: {disposed}")
    print(f"Destroyed: {destroyed}")
    print(f"Released: {released}")