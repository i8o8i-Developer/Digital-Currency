"""
Blockchain.py
Very Small Blockchain With Proof-of-Work and Simple Validation.
"""
import time
import json
from hashlib import sha256
from .Transaction import Transaction
from . import Storage as storage
from .Transaction import verify_tx
from .Wallet import get_balance
from .Consensus import consensus_engine
from .Config import config
from .logger import logger


def sha256d(b: bytes) -> bytes:
    return sha256(sha256(b).digest()).digest()

class Block:
    def __init__(self, index: int, prev_hash: str, transactions: list, nonce=0, timestamp=None):
        self.index = index
        self.prev_hash = prev_hash
        self.transactions = transactions
        self.nonce = nonce
        self.timestamp = timestamp or int(time.time())

    def to_dict(self):
        return {
            'index': self.index,
            'prev_hash': self.prev_hash,
            'transactions': [t.to_dict() for t in self.transactions],
            'nonce': self.nonce,
            'timestamp': self.timestamp
        }

    def hash(self):
        return sha256(json.dumps(self.to_dict(), sort_keys=True).encode()).hexdigest()


class Blockchain:
    def __init__(self, difficulty=None):
        self.chain = []
        self.difficulty = difficulty or config.get('blockchain.difficulty', 3)
        self.utxo = {}  # Map Addr -> list Of (txid, vout, amount)
        self.mempool = []  # list of Transaction
        self.last_block_time = time.time()
        storage.init_db()
        self.create_genesis()
        logger.info(f"Initialized BlockChain With {consensus_engine.algorithm.upper()} Consensus")

    def create_genesis(self):
        coinbase = Transaction([], [])
        b = Block(0, '0'*64, [coinbase], nonce=0)
        self.chain.append(b)
        # Persist Genesis
        storage.save_block(b.index, b.hash(), b.prev_hash, json.dumps(b.to_dict()), b.nonce, b.timestamp)

    def add_block(self, block: Block, producer_address: str = None) -> bool:
        if block.prev_hash != self.chain[-1].hash():
            logger.warning(f"Invalid Previous Hash For Block {block.index}")
            return False

        # Validate Consensus Rules
        block_data = {
            'hash': block.hash(),
            'index': block.index,
            'timestamp': block.timestamp
        }
        if not consensus_engine.validate_block(block_data, producer_address):
            logger.warning(f"Block {block.index} Failed Consensus Validation")
            return False

        # Validate Transactions
        for tx in block.transactions:
            ok, reason = True, ''
            try:
                v, r = verify_tx(tx)
                ok, reason = v, r
            except Exception as e:
                ok, reason = False, f'verify-exception: {str(e)}'
            if not ok:
                logger.warning(f"Invalid Transaction In Block {block.index}: {reason}")
                return False

        self.chain.append(block)
        current_time = time.time()
        self.last_block_time = current_time

        # Persist
        storage.save_block(block.index, block.hash(), block.prev_hash, json.dumps(block.to_dict()), block.nonce, block.timestamp)
        logger.info(f"Added Block {block.index} With {len(block.transactions)} Transactions")

        # Update UTXOs: Remove Spent Inputs And Add Outputs
        for tx in block.transactions:
            txid = tx.txid()
            # Remove Inputs
            for inp in tx.vin:
                storage.remove_utxo(inp.txid, inp.vout)
            # Add Outputs
            for i, out in enumerate(tx.vout):
                storage.add_utxo(txid, i, out.address, out.value)

        # Adjust Difficulty If Needed
        if consensus_engine.should_adjust_difficulty():
            target_time = consensus_engine.get_target_block_time()
            actual_time = current_time - self.last_block_time
            self.difficulty = consensus_engine.calculate_difficulty(self.difficulty, int(actual_time), target_time)

        # Advance Consensus Round
        consensus_engine.advance_round()

        return True

    def mine_block(self, txs: list, producer_address: str = None) -> Block:
        """Mine A New Block Using Current Consensus Algorithm."""
        index = len(self.chain)
        prev = self.chain[-1].hash()

        if consensus_engine.algorithm == 'pow':
            # Traditional PoW Mining
            nonce = 0
            while True:
                b = Block(index, prev, txs, nonce)
                h = b.hash()
                if h.startswith('0'*self.difficulty):
                    return b
                nonce += 1
        else:
            # For PoS/DPoS, Block Production Is Different
            producer = producer_address or consensus_engine.select_block_producer()
            if producer:
                # Create Block Immediately (No Mining Required)
                b = Block(index, prev, txs, nonce=0)
                logger.info(f"Produced Block {index} By {producer} Using {consensus_engine.algorithm.upper()}")
                return b
            else:
                # Fallback To PoW If No Producer Selected
                logger.warning("No Block Producer Selected, Falling Back To PoW")
                nonce = 0
                while True:
                    b = Block(index, prev, txs, nonce)
                    h = b.hash()
                    if h.startswith('0'*self.difficulty):
                        return b
                    nonce += 1

    def submit_tx(self, tx: Transaction):
        ok, reason = verify_tx(tx)
        if not ok:
            return False, reason
        # Simple Duplicate Check
        if any(t.txid() == tx.txid() for t in self.mempool):
            return False, 'duplicate'
        self.mempool.append(tx)
        return True, ''

    def prepare_block_for_miner(self, miner_address: str, reward: int = None) -> list:
        """Create CoinBase Tx Paying Reward To Miner And Include Mempool Txs."""
        from .Transaction import TxOutput

        # Use Consensus Engine To Determine Reward
        if reward is None:
            reward = consensus_engine.get_block_reward(miner_address)

        coinbase = Transaction([], [TxOutput(reward, miner_address)])
        # Include Mempool Txs
        txs = [coinbase] + list(self.mempool)
        logger.info(f"Prepared Block For {miner_address} With Reward {reward} And {len(self.mempool)} Mempool Txs")
        return txs

    def clear_mempool(self, included_txids: list):
        self.mempool = [t for t in self.mempool if t.txid() not in included_txids]