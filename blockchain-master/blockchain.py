import hashlib
import json
from time import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request


class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()
        # Mint some ChumChange and give it to users
        self.current_transactions.append({
            'sender': '0',
            'recipient': 'BradyGroharing',
            'amount': 50,
        })
        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)

    def register_node(self, address: str) -> None:
        """
        Add a new node to the list of nodes

        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain: List[Dict[str, Any]]) -> bool:
        """
        Determine if a given blockchain is valid

        :param chain: A blockchain
        :return: True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self) -> bool:
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.

        :return: True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof: int, previous_hash: Optional[str]) -> Dict[str, Any]:
        """
        Create a new Block in the Blockchain

        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :return: New Block
        """
        full_file_path = '../backups/chum_change_backup.txt'

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        write_file = open(full_file_path, 'w')
        write_file.write(str(self.chain))

        return block

    def new_transaction(self, sender: str, recipient: str, amount: int) -> int:
        """
        Creates a new transaction to go into the next mined Block

        :param sender: Address of the Sender
        :param recipient: Address of the Recipient
        :param amount: Amount
        :return: The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self) -> Dict[str, Any]:
        return self.chain[-1]

    @staticmethod
    def hash(block: Dict[str, Any]) -> str:
        """
        Creates a SHA-256 hash of a Block

        :param block: Block
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof: int) -> int:
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof: int, proof: int) -> bool:
        """
        Validates the Proof

        :param last_proof: Previous Proof
        :param proof: Current Proof
        :return: True if correct, False if not.
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


    def approve_current_transactions(self, senders_wallets):
        """
        Allows or disallows transactions in the block being mined

        :param senders_wallets: A dict with all the {senders, amount_they_own}
        """
        transactions = self.current_transactions
        for i in range(len(transactions)) :
            current_sender = transactions[i]['sender']
            current_amount = transactions[i]['amount']
            # If they're not in senders_wallets it means they have no money
            if current_sender in senders_wallets:
                # Do they have less in their wallet than they're spending?
                if senders_wallets[current_sender] < current_amount:
                    self.current_transactions.remove(transactions[i])
            else:
                self.current_transactions.remove(transactions[i])


    def validate_transactions(self):
        """
         Validates the current transactions

         """
        all_senders_in_block = []
        all_recipients_in_block = []
        # senders_wallets = {}
        # Gets all the senders in the current transaction
        for i in range(len(self.current_transactions)) :
            values = self.current_transactions[i]
            current_sender = values['sender']
            current_recipient = values['recipient']
            if current_sender not in all_senders_in_block:
                all_senders_in_block.append(current_sender)
                all_recipients_in_block.append(current_recipient)

        blockchain.approve_current_transactions(blockchain.get_balance(all_senders_in_block))


    def get_balance(self, users):
        """
         Gets the balance of all the wallets provided by the param

        :param users: A list of all the senders whose balances we want
         """
        senders_wallets = {}
        # This is supposed to figure out how much each sender has based on how much they've sent and received
        for i in range(len(self.chain)):
            transactions = self.chain[i]['transactions']
            # for each transaction in each block on the chain
            for j in range(len(transactions)):
                current_sender = transactions[j]['sender']
                current_amount = transactions[j]['amount']
                current_recipient = transactions[j]['recipient']
                # Did they get money?
                if current_recipient in users:
                    if current_sender in senders_wallets.keys():
                        senders_wallets[current_recipient] = senders_wallets[current_recipient] + current_amount
                    else:
                        senders_wallets[current_recipient] = current_amount
                # Did they spend money?
                elif current_sender in users:
                    senders_wallets[current_sender] = senders_wallets[current_sender] - current_amount
        return senders_wallets










# Instantiate the Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

@app.route('/balance', methods=['POST'])
def balance():
    values = request.get_json()
    # Check that the required fields are in the POST'ed data
    required = ['user']
    if not all(k in values for k in required):
        return 'Missing value', 400

    # Create a new Transaction
    index = blockchain.get_balance(values['user'])

    response = {'message': f'{index}'}
    return jsonify(response), 201


@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    blockchain.validate_transactions()
    proof = blockchain.proof_of_work(last_proof)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )
    # print(proof)
    # Forge the new Block by adding it to the chain
    block = blockchain.new_block(proof, last_proof)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
