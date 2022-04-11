from argparse import ArgumentParser
from uuid import uuid4

from flask import Flask, jsonify, request

from blockchain import Blockchain

app = Flask(__name__)  # Instantiate the Node
node_identifier = str(uuid4()).replace('-', '')  # Generate a globally unique address for this node
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])  # This route is called by the miner when they want to mine a new block.
def mine() -> tuple:
    """ Mine a new block.

    This function does the following:
        1. Gets the last block from the chain.
        2. Get the proof of work for the last block.
        3. Create a new block with the proof of work.
        4. Add the new block to the chain.
        5. Broadcast the new block to all other nodes.

    Returns: The proof of work for the new block.
        The miner will then use this proof of work to find the hash of the previous block. This hash will be used to
        create the new block. The miner will then send this hash to the node that will verify the hash.
    """
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,  # The miner's address will be the recipient of the coin.
        amount=1,  # Reward for mining a new coin.
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
def new_transaction() -> tuple:
    """ Add a new transaction to the blockchain.
            This route is called by the miner when they want to add a new transaction to the blockchain. The miner will
            send the transaction to the node that will add it to the chain.

    This function does the following:
        1. Get the data from the request.
        2. Check that the data is valid.
        3. Add the transaction to the list of transactions.
        4. Return a response with the index of the new transaction.

    Returns:
        The index of the new transaction.
    """
    values = request.get_json()

    # Check that the required fields are in the POST'ed data. If not, return a 400 Bad Request.
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction and add it to the list of transactions.
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201  # 201 Created


@app.route('/chain', methods=['GET'])
def full_chain() -> tuple:
    """ Get the full chain.
            This route is called by the miner when they want to get the full chain. The miner will send this request to
            the node that will send the chain to the miner.  The miner will then send the chain to the node that will
            verify the chain.

    This function does the following:
        1. Get the chain.
        2. Return the chain.

    Returns:
        The chain.
    """
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes() -> tuple:
    """ Register a new node.
            This route is called by the miner when they want to register a new node. The miner will send the node to
            the node that will add it to the list of nodes.

    This function does the following:
        1. Get the data from the request.
        2. Check that the data is valid.
        3. Add the node to the list of nodes.
        4. Return a response with the list of nodes.

    Returns:
        The list of nodes.
    """
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
def consensus() -> tuple:
    """ Resolve conflicts.

    This function does the following:
        1. Call the consensus function to resolve conflicts.
        2. Return a response with the chain.

    Returns:
        The chain.
    """
    replaced = blockchain.resolve_conflicts()  # Returns True if replaced, then the chain is replaced.

    if replaced:  # If the chain was replaced, return the new chain.
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:  # Otherwise, return the old chain.
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    parser = ArgumentParser()  # Create a parser object. This is used to parse the command line arguments.
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()  # Parse the arguments. This returns an object with the arguments as attributes.
    port = args.port  # Get the port from the arguments. This is the port that the node will listen on.

    app.run(port=port)
