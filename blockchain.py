
import time
import json
import hashlib
from urllib.parse import urlparse
import requests

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_data = {
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()


class Blockchain:
    difficulty = 4

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.nodes = set()
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "0")
        self.chain.append(genesis_block)

    def get_last_block(self):
        return self.chain[-1]

    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def add_block(self, block, proof):
        previous_hash = self.get_last_block().hash
        if previous_hash != block.previous_hash:
            return False
        if not proof.startswith('0' * Blockchain.difficulty):
            return False
        if proof != block.compute_hash():
            return False
        block.hash = proof
        self.chain.append(block)
        return True

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def mine(self, miner_address=None):
        if not self.unconfirmed_transactions:
            return False

        if miner_address:
            reward_tx = {
                "sender": "0",
                "recipient": miner_address,
                "amount": 100
            }
            self.unconfirmed_transactions.append(reward_tx)

        last_block = self.get_last_block()
        new_block = Block(
            index=last_block.index + 1,
            transactions=self.unconfirmed_transactions,
            timestamp=time.time(),
            previous_hash=last_block.hash
        )
        proof = self.proof_of_work(new_block)
        added = self.add_block(new_block, proof)
        if not added:
            return False
        self.unconfirmed_transactions = []
        return new_block.index

    def is_chain_valid(self, chain=None):
        if chain is None:
            chain = self.chain

        for i in range(1, len(chain)):
            current = chain[i]
            previous = chain[i - 1]
            if current.previous_hash != previous.hash:
                return False
            if not current.hash.startswith('0' * Blockchain.difficulty):
                return False
            if current.hash != current.compute_hash():
                return False
        return True

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def resolve_conflicts(self):
        longest_chain = None
        max_length = len(self.chain)

        for node in self.nodes:
            try:
                response = requests.get(f'http://{node}/chain')
                if response.status_code == 200:
                    length = response.json()['length']
                    chain_data = response.json()['chain']

                    chain = []
                    for block_data in chain_data:
                        block = Block(
                            index=block_data['index'],
                            transactions=block_data['transactions'],
                            timestamp=block_data['timestamp'],
                            previous_hash=block_data['previous_hash'],
                            nonce=block_data['nonce']
                        )
                        block.hash = block_data['hash']
                        chain.append(block)

                    if length > max_length and self.is_chain_valid(chain):
                        max_length = length
                        longest_chain = chain
            except Exception:
                continue

        if longest_chain:
            self.chain = longest_chain
            return True

        return False
