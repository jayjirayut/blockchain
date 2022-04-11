"""
This is a blockchain that is used to create a cryptocurrency.
    It is a chain of blocks that are linked together.
    Each block contains a transaction.
    Each transaction contains a sender, a recipient, and a value.

The blockchain is a list of blocks.
    The first block is called the genesis block.
    The genesis block is the first block in the chain.
    The genesis block has no previous block.
    The genesis block has no transactions.

The blockchain is created by adding blocks to the list.
    The blocks are added to the end of the list.
    The last block in the list is the most recent block.
    The first block in the list is the oldest block.

The blockchain is validated by checking the hashes of each block.
    The hashes of each block are calculated by hashing the previous block's hash.
"""

import hashlib  # Used to calculate the hash of a block.
import json  # Used to convert the block into a string.
from time import time  # Used to calculate the time of a block.
from urllib.parse import urlparse  # Used to parse the url. The url is used to identify the node. The node is used to
# connect to the blockchain.
from uuid import uuid4  # Used to generate a unique ID for a block.

import requests  # Used to send a request to a node.
from flask import Flask, jsonify, request  # Used to create a web server.


class Blockchain:
    """Blockchain class.

    Attributes:
        current_transactions (list): List of current transactions.
            The transactions are added to the list when a new block is created.
            The transactions are removed from the list when a block is added to the chain.
        chain (list): List of blocks.
        nodes (set): Set of nodes.
            The nodes are used to connect to the blockchain.
    """

    def __init__(self):
        """Initialize blockchain."""
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)  # Genesis block is the first block in the chain. It has no
        # previous block. It has no transactions. It has a proof of 100. It has a hash of 1. It has a timestamp of 0.

    def register_node(self, address) -> None:
        """
        Add a new node to the list of nodes.

        Args:
            address: Address of node.
        """
        parsed_url = urlparse(address)  # Parse the address into a URL object.
        self.nodes.add(parsed_url.netloc)  # Add the netloc to the set of nodes. The netloc is the hostname of the
        # node. The hostname is the name of the node. The name of the node is the address of the node.

    def valid_chain(self, chain: list) -> bool:
        """
        Determine if a given blockchain is valid. This function is used by the consensus algorithm. The consensus
        algorithm is used by all nodes in the network.

        1. Check if the genesis block is valid.
        2. Check if the previous hash of the current block is the same as the previous block's hash.
        3. Check if the current block's hash is valid.
        4. Check if the proof of work is valid.

        Args:
            chain: A list of blocks.

        Returns:
            True if the chain is valid, False if not.
        """
        last_block = chain[0]   # The first block in the chain is the genesis block.
        current_index = 1   # Start at the second block.

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False  # The previous hash of the block is not correct. The chain is not valid.

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False  # The proof of work is not correct. The chain is not valid.

            # This is used to check the next block.
            last_block = block  # Set the last block to the current block.
            current_index += 1  # Increment the index.

        return True  # The chain is valid.

    def resolve_conflicts(self) -> bool:
        """
        This is our Consensus Algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.

        1. Get the chains from all the nodes in the network.
                The chains are stored in a dictionary.The key is the node's address.
        2. Pick the longest chain.
                The chain with the most blocks is the longest chain.
        3. If the chain we are on is not the longest, we replace our chain with the longest one.

        Returns:
            True if our chain was replaced, False if not.
        """

        neighbours = self.nodes  # Get the list of nodes.
        new_chain = None  # The new chain. This is the chain that will replace the current chain.

        max_length = len(self.chain)  # Get the length of our chain.

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            # Get the chain from the node. The response is a JSON object.
            response = requests.get(f'https://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length  # Set the new length.
                    new_chain = chain    # Set the new chain.

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain  # Replace the current chain with the new one.
            return True  # Return True to indicate that we replaced the chain.

        return False  # Return False to indicate that we did not replace the chain.

    def new_block(self, proof, previous_hash=None) -> dict:
        """
        Create a new Block in the Blockchain. The block contains the transactions and the proof of work.

        1. Create a new block.
        2. Add the block to the chain.
        3. Return the block.

        Args:
            proof: The proof of work.
                A number generated by the Proof of Work algorithm.
            previous_hash: (Optional) The hash of the previous block.
                If not specified, the previous block's hash will be used. This is used to link the new block to the
                previous block.

        Returns:
            The new block.
        """
        block = {
            'index': len(self.chain) + 1,  # Index of the block, the number of blocks in the chain. Starts at 1.
            'timestamp': time(),  # Timestamp of the block.
            'transactions': self.current_transactions,  # List of transactions.
            'proof': proof,  # Proof of work. The number of leading zeros in the hash of the previous block.
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions to an empty list.
        self.current_transactions = []  # This is done so that the transactions are not added to the next block.

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block.

        param sender: Address of the Sender.
        param recipient: Address of the Recipient.
        param amount: Amount.
        :return: The index of the Block that will hold this transaction.
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]  # This is the block that is currently being mined.

    @staticmethod
    def hash(block: dict) -> str:
        """
        Creates SHA-256 hash of a Block

        1. Make sure that the Dictionary is Ordered. (Dictionaries are not ordered by default) This is important because
                the hash is based on the order of the keys in the dictionary. If the order is not correct, the hash will
                be different. This is important because the hash is used to verify the integrity of the chain.
                If the hash is not correct, the chain will be invalid.
        2. Convert the dictionary to a JSON string.
        3. Use the hashlib.sha256 function to get a hash.
        4. Represent the hash as a hexadecimal string.
        5. Return the hexadecimal string.

        Args:
            block: Block to be hashed.

        Returns:
            SHA-256 hash of the block.
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes.
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
        """

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof) -> bool:
        """
        Validates the Proof of Work: Does hash(last_proof, proof) contain 4 leading zeroes?

        Args:
            last_proof: Previous Proof.
            proof: Current Proof.

        Returns:
            True if correct, False if not.
        """

        guess = f'{last_proof}{proof}'.encode()  # Create a string containing the last proof and the current proof.
        guess_hash = hashlib.sha256(guess).hexdigest()  # Create SHA-256 hash of the string.
        return guess_hash[:4] == "0000"  # Check if the hash begins with 4 leading zeroes.


# Instantiate the Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

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

    # Check that the required fields are in the POSTed data
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

    app.run(port=port)
