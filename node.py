
from flask import Flask, request, jsonify
from flasgger import Swagger
from blockchain import Blockchain

app = Flask(__name__)
swagger = Swagger(app)
blockchain = Blockchain()


@app.route('/chain', methods=['GET'])
def get_chain():
    """
    Get the full blockchain
    ---
    tags:
      - Blockchain
    responses:
      200:
        description: Returns the full blockchain
    """
    chain_data = [block.__dict__ for block in blockchain.chain]
    return jsonify({
        "length": len(chain_data),
        "chain": chain_data
    }), 200


@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    """
    Mine unconfirmed transactions and reward the miner
    ---
    tags:
      - Mining
    parameters:
      - name: miner
        in: query
        type: string
        required: true
        description: Wallet address of the miner
    responses:
      201:
        description: Block mined successfully
      200:
        description: No transactions to mine
    """
    miner_address = request.args.get("miner")
    result = blockchain.mine(miner_address)
    if not result:
        return jsonify({"message": "No transactions to mine"}), 200
    return jsonify({"message": f"Block #{result} has been mined."}), 201


@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    """
    Add a new transaction
    ---
    tags:
      - Transactions
    parameters:
      - in: body
        name: transaction
        required: true
        schema:
          type: object
          required:
            - sender
            - recipient
            - amount
          properties:
            sender:
              type: string
              example: Alice
            recipient:
              type: string
              example: Bob
            amount:
              type: number
              example: 10
    responses:
      201:
        description: Transaction added successfully
      400:
        description: Invalid transaction data
      500:
        description: Internal server error
    """
    try:
        tx_data = request.get_json()
        print("Received transaction data:", tx_data)

        required_fields = ["sender", "recipient", "amount"]
        if not tx_data or not all(field in tx_data for field in required_fields):
            return jsonify({"error": "Invalid transaction data. Required fields: sender, recipient, amount"}), 400

        blockchain.add_new_transaction(tx_data)
        return jsonify({"message": "Transaction added successfully"}), 201
    except Exception as e:
        print("Error while processing transaction:", str(e))
        return jsonify({"error": "Internal server error"}), 500


@app.route('/validate_chain', methods=['GET'])
def validate_chain():
    """
    Validate the integrity of the blockchain
    ---
    tags:
      - Blockchain
    responses:
      200:
        description: Returns whether the blockchain is valid
    """
    is_valid = blockchain.is_chain_valid()
    return jsonify({
        "valid": is_valid,
        "message": "Blockchain is valid." if is_valid else "Blockchain is invalid!"
    }), 200


@app.route('/register_node', methods=['POST'])
def register_node():
    """
    Register a new peer node
    ---
    tags:
      - Network
    parameters:
      - in: body
        name: node
        required: true
        schema:
          type: object
          required:
            - address
          properties:
            address:
              type: string
              example: http://127.0.0.1:5001
    responses:
      201:
        description: Node registered successfully
      400:
        description: Invalid node data
    """
    data = request.get_json()
    node_address = data.get("address")
    if not node_address:
        return jsonify({"error": "Invalid data. 'address' is required"}), 400
    blockchain.register_node(node_address)
    return jsonify({
        "message": "Node registered successfully",
        "total_nodes": list(blockchain.nodes)
    }), 201


@app.route('/resolve_conflicts', methods=['GET'])
def resolve_conflicts():
    """
    Resolve conflicts between different nodes (Consensus)
    ---
    tags:
      - Network
    responses:
      200:
        description: Conflict resolution result
    """
    replaced = blockchain.resolve_conflicts()
    return jsonify({
        "replaced": replaced,
        "message": "Our chain was replaced." if replaced else "Our chain is authoritative.",
        "chain": [block.__dict__ for block in blockchain.chain]
    }), 200


if __name__ == '__main__':
    app.run(port=5000)
