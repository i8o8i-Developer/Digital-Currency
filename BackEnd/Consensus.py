"""
Consensus.py
Advanced Consensus Mechanisms For i8o8iCoin.
Supports PoW, PoS, and DPoS.
"""
import time
import random
from hashlib import sha256
from typing import List, Dict, Optional
from . import Storage as storage
from .Wallet import get_balance
from .Config import config
from .logger import logger

class ConsensusEngine:
    """Main Consensus Engine Supporting Multiple Algorithms."""

    def __init__(self, algorithm='pow'):
        self.algorithm = algorithm
        self.validators: Dict[str, int] = {}  # address -> stake
        self.delegates: List[str] = []
        self.current_round = 0
        self.round_start_time = time.time()

    def set_algorithm(self, algorithm: str):
        """Switch Consensus Algorithm."""
        if algorithm not in ['pow', 'pos', 'dpos']:
            raise ValueError(f"Unsupported Algorithm: {algorithm}")
        self.algorithm = algorithm
        logger.info(f"Switched To {algorithm.upper()} Consensus")

    def validate_block(self, block_data: Dict, miner_address: str = None) -> bool:
        """Validate A Block According To Current Consensus Rules."""
        if self.algorithm == 'pow':
            return self._validate_pow(block_data)
        elif self.algorithm == 'pos':
            return self._validate_pos(block_data, miner_address)
        elif self.algorithm == 'dpos':
            return self._validate_dpos(block_data, miner_address)
        return False

    def select_block_producer(self) -> str:
        """Select The Next Block Producer Based On Consensus Algorithm."""
        if self.algorithm == 'pow':
            return None  # Any Miner Can Produce
        elif self.algorithm == 'pos':
            return self._select_pos_producer()
        elif self.algorithm == 'dpos':
            return self._select_dpos_producer()
        return None

    def _validate_pow(self, block_data: Dict) -> bool:
        """Validate Proof-of-Work Block."""
        difficulty = config.get('blockchain.difficulty', 4)
        block_hash = block_data.get('hash', '')
        return block_hash.startswith('0' * difficulty)

    def _validate_pos(self, block_data: Dict, producer_address: str) -> bool:
        """Validate Proof-of-Stake Block."""
        if not producer_address:
            return False

        stake = self._get_stake(producer_address)
        min_stake = config.get('consensus.pos_stake_minimum', 1000)

        if stake < min_stake:
            return False

        # Simple Stake-Weighted Validation
        # In Real PoS, This Would Be More Complex
        block_hash = block_data.get('hash', '')
        target = 2**256 // (stake // min_stake)
        block_int = int(block_hash, 16)
        return block_int < target

    def _validate_dpos(self, block_data: Dict, producer_address: str) -> bool:
        """Validate Delegated Proof-of-Stake Block."""
        if not producer_address:
            return False

        if producer_address not in self.delegates:
            return False

        # Check If It's This Delegate's Turn
        expected_producer = self._get_round_producer()
        return producer_address == expected_producer

    def _select_pos_producer(self) -> str:
        """Select A Block Producer Using Proof-of-Stake."""
        total_stake = sum(self.validators.values())
        if total_stake == 0:
            return None

        # Weighted Random Selection
        pick = random.randint(0, total_stake - 1)
        current = 0
        for address, stake in self.validators.items():
            current += stake
            if current > pick:
                return address
        return None

    def _select_dpos_producer(self) -> str:
        """Select A Block Producer Using DPoS."""
        if not self.delegates:
            self._update_delegates()

        round_blocks = config.get('consensus.dpos_round_blocks', 21)
        producer_index = (self.current_round // round_blocks) % len(self.delegates)
        return self.delegates[producer_index]

    def _get_round_producer(self) -> str:
        """Get the producer for current round."""
        round_blocks = config.get('consensus.dpos_round_blocks', 21)
        producer_index = (self.current_round % round_blocks) % len(self.delegates)
        return self.delegates[producer_index] if self.delegates else None

    def _get_stake(self, address: str) -> int:
        """Get stake for an address."""
        return self.validators.get(address, get_balance(address))

    def update_stake(self, address: str, stake: int):
        """Update stake for an address."""
        self.validators[address] = stake

    def _update_delegates(self):
        """Update The List of Delegates Based on Voting Power."""
        # Get All Addresses With Stake
        candidates = []
        for address, stake in self.validators.items():
            candidates.append((address, stake))

        # Sort By Stake (Descending)
        candidates.sort(key=lambda x: x[1], reverse=True)

        # Select Top N Delegates
        num_delegates = config.get('consensus.dpos_delegates', 21)
        self.delegates = [addr for addr, _ in candidates[:num_delegates]]

    def advance_round(self):
        """Advance To The Next Consensus Round."""
        self.current_round += 1
        self.round_start_time = time.time()

        if self.algorithm == 'dpos':
            round_blocks = config.get('consensus.dpos_round_blocks', 21)
            if self.current_round % round_blocks == 0:
                self._update_delegates()

    def get_block_reward(self, producer_address: str = None) -> int:
        """Calculate Block Reward Based on Consensus Algorithm."""
        base_reward = config.get('blockchain.mining_reward', 50)

        if self.algorithm == 'pow':
            return base_reward
        elif self.algorithm == 'pos':
            # Stake-Weighted Reward
            if producer_address:
                total_stake = sum(self.validators.values())
                stake = self._get_stake(producer_address)
                return base_reward * (stake / total_stake) if total_stake > 0 else base_reward
            return base_reward
        elif self.algorithm == 'dpos':
            # Fixed Reward For Delegates
            return base_reward

        return base_reward

    def get_target_block_time(self) -> int:
        """Get Target Block Time For Current Consensus."""
        return config.get('blockchain.block_time_target', 600)

    def should_adjust_difficulty(self) -> bool:
        """Check If Difficulty Should Be Adjusted."""
        return self.algorithm == 'pow'

    def calculate_difficulty(self, current_difficulty: int, actual_time: int, target_time: int) -> int:
        """Calculate New Difficulty For PoW."""
        if self.algorithm != 'pow':
            return current_difficulty

        # Simple Difficulty Adjustment
        ratio = actual_time / target_time
        if ratio < 0.75:
            return min(current_difficulty + 1, 8)  # Increase Difficulty
        elif ratio > 1.25:
            return max(current_difficulty - 1, 1)  # Decrease Difficulty
        return current_difficulty


class VotingSystem:
    """Voting System For DPoS."""

    def __init__(self):
        self.votes: Dict[str, Dict[str, int]] = {}  # voter -> {delegate: weight}

    def vote(self, voter: str, delegate: str, weight: int = 1):
        """Cast A Vote For A Delegate."""
        if voter not in self.votes:
            self.votes[voter] = {}
        self.votes[voter][delegate] = weight

    def unvote(self, voter: str, delegate: str):
        """Remove Vote For A Delegate."""
        if voter in self.votes and delegate in self.votes[voter]:
            del self.votes[voter][delegate]

    def get_delegate_votes(self, delegate: str) -> int:
        """Get Total Votes For A Delegate."""
        total = 0
        for voter_votes in self.votes.values():
            total += voter_votes.get(delegate, 0)
        return total

    def get_voter_votes(self, voter: str) -> Dict[str, int]:
        """Get Votes Cast By A Voter."""
        return self.votes.get(voter, {})


# Global Instances
consensus_engine = ConsensusEngine(config.get('consensus.algorithm', 'pow'))
voting_system = VotingSystem()