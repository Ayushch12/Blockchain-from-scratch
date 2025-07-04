import hashlib
import json

def hash_block(block_dict):
    """
    Returns the SHA-256 hash of a block dictionary.
    """
    block_string = json.dumps(block_dict, sort_keys=True)
    return hashlib.sha256(block_string.encode()).hexdigest()

def is_valid_proof(block, block_hash, difficulty):
    """
    Check if a block hash is valid: starts with 'difficulty' zeros
    and is the correct hash of the block.
    """
    return (block_hash.startswith('0' * difficulty) and
            block_hash == hash_block(block.__dict__))
