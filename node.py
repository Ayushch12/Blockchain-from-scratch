from flask import Flask, request, jsonify
from blockchain import Blockchain

app = Flask(__name__)
blockchain = Blockchain()

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return jsonify({
        "length": len(chain_data),
        "chain": chain_data
    }), 200

@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return jsonify({"message": "No transactions to mine"}), 200
    return jsonify({"message": f"Block #{result} has been mined."}), 201

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    try:
        tx_data = request.get_json()
        print("Received transaction data:", tx_data)  # debug log

        required_fields = ["sender", "recipient", "amount"]
        if not tx_data or not all(field in tx_data for field in required_fields):
            return jsonify({"error": "Invalid transaction data. Required fields: sender, recipient, amount"}), 400

        blockchain.add_new_transaction(tx_data)
        return jsonify({"message": "Transaction added successfully"}), 201
    except Exception as e:
        print("Error while processing transaction:", str(e))
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(port=5000)
