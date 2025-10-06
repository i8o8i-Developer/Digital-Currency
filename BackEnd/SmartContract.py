"""
SmartContract.py
Basic Smart Contract System For i8o8iCoin.
Supports Simple Scripts And Programmable Money.
"""
import json
import time
from hashlib import sha256
from typing import List, Dict, Any, Optional
from .Crypto import ecdsa_verify
from . import Storage as storage
from .logger import logger

class ScriptEngine:
    """Simple Script Engine For Smart Contracts."""

    OPCODES = {
        'OP_DUP': 0x76,
        'OP_HASH160': 0xA9,
        'OP_EQUALVERIFY': 0x88,
        'OP_CHECKSIG': 0xAC,
        'OP_CHECKMULTISIG': 0xAE,
        'OP_IF': 0x63,
        'OP_ELSE': 0x67,
        'OP_ENDIF': 0x68,
        'OP_VERIFY': 0x69,
        'OP_RETURN': 0x6A,
        'OP_CHECKLOCKTIMEVERIFY': 0xB1,
        'OP_CHECKSEQUENCEVERIFY': 0xB2,
    }

    @staticmethod
    def execute(script: bytes, stack: List[bytes], tx_data: Dict) -> bool:
        """Execute A Script And Return Success/Failure."""
        try:
            opcodes = script
            pc = 0
            alt_stack = []

            while pc < len(opcodes):
                opcode = opcodes[pc]
                pc += 1

                if opcode == ScriptEngine.OPCODES['OP_DUP']:
                    if not stack:
                        return False
                    stack.append(stack[-1])
                elif opcode == ScriptEngine.OPCODES['OP_HASH160']:
                    if not stack:
                        return False
                    data = stack.pop()
                    hash160 = sha256(sha256(data).digest()).digest()[:20]
                    stack.append(hash160)
                elif opcode == ScriptEngine.OPCODES['OP_EQUALVERIFY']:
                    if len(stack) < 2:
                        return False
                    a, b = stack.pop(), stack.pop()
                    if a != b:
                        return False
                elif opcode == ScriptEngine.OPCODES['OP_CHECKSIG']:
                    if len(stack) < 2:
                        return False
                    pubkey, sig = stack.pop(), stack.pop()
                    message = tx_data.get('message', b'')
                    if not ecdsa_verify(pubkey.hex(), message, sig.hex()):
                        return False
                    stack.append(b'\x01')
                elif opcode == ScriptEngine.OPCODES['OP_CHECKMULTISIG']:
                    # Simplified Multi-Sig Implementation
                    if len(stack) < 4:
                        return False
                    n = stack.pop()[0]
                    pubkeys = []
                    for _ in range(n):
                        pubkeys.append(stack.pop())
                    m = stack.pop()[0]
                    sigs = []
                    for _ in range(m):
                        sigs.append(stack.pop())

                    valid_sigs = 0
                    message = tx_data.get('message', b'')
                    for sig in sigs:
                        for pubkey in pubkeys:
                            if ecdsa_verify(pubkey.hex(), message, sig.hex()):
                                valid_sigs += 1
                                break

                    if valid_sigs < m:
                        return False
                    stack.append(b'\x01')
                elif opcode == ScriptEngine.OPCODES['OP_CHECKLOCKTIMEVERIFY']:
                    if not stack:
                        return False
                    locktime = int.from_bytes(stack[-1], 'little')
                    current_time = tx_data.get('locktime', 0)
                    if current_time < locktime:
                        return False
                elif opcode == ScriptEngine.OPCODES['OP_CHECKSEQUENCEVERIFY']:
                    # Sequence Number Verification
                    if not stack:
                        return False
                    sequence = int.from_bytes(stack[-1], 'little')
                    tx_sequence = tx_data.get('sequence', 0xFFFFFFFF)
                    if tx_sequence < sequence:
                        return False
                elif opcode == ScriptEngine.OPCODES['OP_VERIFY']:
                    if not stack or stack.pop() == b'\x00':
                        return False
                elif opcode == ScriptEngine.OPCODES['OP_RETURN']:
                    # Mark Script As Invalid (Data Carrier)
                    return False
                elif opcode <= 0x4B:  # Push Data
                    data_len = opcode
                    if pc + data_len > len(opcodes):
                        return False
                    data = opcodes[pc:pc + data_len]
                    stack.append(data)
                    pc += data_len
                else:
                    # Unknown Opcode
                    return False

            return len(stack) > 0 and stack[-1] != b'\x00'

        except Exception as e:
            logger.error(f"Script Execution Error: {e}")
            return False


class SmartContract:
    """Smart Contract Class."""

    GAS_COSTS = {
        'OP_DUP': 3,
        'OP_HASH160': 5,
        'OP_EQUALVERIFY': 3,
        'OP_CHECKSIG': 10,
        'OP_CHECKMULTISIG': 20,
        'OP_IF': 3,
        'OP_ELSE': 3,
        'OP_ENDIF': 3,
        'OP_VERIFY': 3,
        'OP_RETURN': 0,
        'OP_CHECKLOCKTIMEVERIFY': 5,
        'OP_CHECKSEQUENCEVERIFY': 5,
        'transfer': 50,
        'balanceOf': 20,
        'totalSupply': 20,
        'mint': 100,
        'burn': 50,
    }

    def __init__(self, contract_id: str, code: bytes, owner: str, state: Dict = None):
        self.contract_id = contract_id
        self.code = code
        self.owner = owner
        self.state = state or {}
        self.balance = 0
        self.created_at = None
        self.updated_at = None
        self.gas_used = 0

    def to_dict(self) -> Dict:
        return {
            'contract_id': self.contract_id,
            'code': self.code.hex(),
            'owner': self.owner,
            'state': self.state,
            'balance': self.balance,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'SmartContract':
        contract = cls(
            data['contract_id'],
            bytes.fromhex(data['code']),
            data['owner'],
            data['state']
        )
        contract.balance = data['balance']
        contract.created_at = data['created_at']
        contract.updated_at = data['updated_at']
        return contract

    def execute(self, method: str, params: List[Any], caller: str, value: int = 0, gas_limit: int = 100000) -> Dict:
        """Execute A Contract Method With Gas Tracking."""
        gas_used = 0
        try:
            # Check Gas Limit
            if gas_limit < 1000:
                return {'error': 'Gas Limit Too Low', 'gas_used': gas_used}

            # ERC-20 Standard Methods
            if method == 'name':
                gas_used += 20
                return {'result': self.state.get('name', ''), 'gas_used': gas_used}
            elif method == 'symbol':
                gas_used += 20
                return {'result': self.state.get('symbol', ''), 'gas_used': gas_used}
            elif method == 'decimals':
                gas_used += 20
                return {'result': self.state.get('decimals', 18), 'gas_used': gas_used}
            elif method == 'totalSupply':
                gas_used += 20
                return {'result': self._total_supply(), 'gas_used': gas_used}
            elif method == 'balanceOf':
                gas_used += 20
                return {'result': self._balance_of(params[0]), 'gas_used': gas_used}
            elif method == 'transfer':
                gas_used += self.GAS_COSTS.get('transfer', 50)
                if gas_used > gas_limit:
                    return {'error': 'Out of gas', 'gas_used': gas_used}
                result = self._transfer(caller, params[0], params[1])
                result['gas_used'] = gas_used
                return result
            elif method == 'approve':
                gas_used += 30
                if gas_used > gas_limit:
                    return {'error': 'Out of gas', 'gas_used': gas_used}
                result = self._approve(caller, params[0], params[1])
                result['gas_used'] = gas_used
                return result
            elif method == 'allowance':
                gas_used += 20
                return {'result': self._allowance(params[0], params[1]), 'gas_used': gas_used}
            elif method == 'transferFrom':
                gas_used += 60
                if gas_used > gas_limit:
                    return {'error': 'Out of gas', 'gas_used': gas_used}
                result = self._transfer_from(caller, params[0], params[1], params[2])
                result['gas_used'] = gas_used
                return result
            # Admin methods
            elif method == 'mint':
                gas_used += self.GAS_COSTS.get('mint', 100)
                if gas_used > gas_limit:
                    return {'error': 'Out of gas', 'gas_used': gas_used}
                result = self._mint(caller, params[0], params[1])
                result['gas_used'] = gas_used
                return result
            elif method == 'burn':
                gas_used += self.GAS_COSTS.get('burn', 50)
                if gas_used > gas_limit:
                    return {'error': 'Out of gas', 'gas_used': gas_used}
                result = self._burn(caller, params[0], params[1])
                result['gas_used'] = gas_used
                return result
            else:
                return {'error': f'Unknown Method: {method}', 'gas_used': gas_used}
        except Exception as e:
            logger.error(f"Contract Execution Error: {e}")
            return {'error': str(e), 'gas_used': gas_used}

    def _transfer(self, caller: str, to: str, amount: int) -> Dict:
        """Transfer Tokens."""
        if self.state.get('balances', {}).get(caller, 0) < amount:
            return {'error': 'Insufficient Balance'}
        self.state['balances'][caller] -= amount
        self.state['balances'][to] = self.state['balances'].get(to, 0) + amount
        return {'success': True}

    def _balance_of(self, address: str) -> int:
        """Get Balance of Address."""
        return self.state.get('balances', {}).get(address, 0)

    def _total_supply(self) -> int:
        """Get Total Supply."""
        return self.state.get('total_supply', 0)

    def _mint(self, caller: str, to: str, amount: int) -> Dict:
        """Mint New Tokens (Owner Only)."""
        if caller != self.owner:
            return {'error': 'Unauthorized'}
        self.state['balances'][to] = self.state['balances'].get(to, 0) + amount
        self.state['total_supply'] = self.state.get('total_supply', 0) + amount
        return {'success': True}

    def _burn(self, caller: str, from_addr: str, amount: int) -> Dict:
        """Burn Tokens."""
        if caller != from_addr and caller != self.owner:
            return {'error': 'Unauthorized'}
        if self.state.get('balances', {}).get(from_addr, 0) < amount:
            return {'error': 'Insufficient Balance'}
        self.state['balances'][from_addr] -= amount
        self.state['total_supply'] = self.state.get('total_supply', 0) - amount
        return {'success': True}

    def _approve(self, caller: str, spender: str, amount: int) -> Dict:
        """Approve Spender To Spend Tokens On Behalf Of Caller."""
        if 'allowances' not in self.state:
            self.state['allowances'] = {}
        if caller not in self.state['allowances']:
            self.state['allowances'][caller] = {}
        self.state['allowances'][caller][spender] = amount
        return {'success': True}

    def _allowance(self, owner: str, spender: str) -> int:
        """Get Allowance For Spender."""
        return self.state.get('allowances', {}).get(owner, {}).get(spender, 0)

    def _transfer_from(self, caller: str, sender: str, recipient: str, amount: int) -> Dict:
        """Transfer Tokens From Sender To Recipient Using Allowance."""
        allowance = self._allowance(sender, caller)
        if allowance < amount:
            return {'error': 'Insufficient Allowance'}

        if self.state.get('balances', {}).get(sender, 0) < amount:
            return {'error': 'Insufficient balance'}

        # Update Balances
        self.state['balances'][sender] -= amount
        self.state['balances'][recipient] = self.state['balances'].get(recipient, 0) + amount

        # Update Allowance
        self.state['allowances'][sender][caller] -= amount

        return {'success': True}


class ContractManager:
    """Manager For Smart Contracts."""

    def __init__(self):
        self.contracts: Dict[str, SmartContract] = {}
        self._load_contracts()

    def _load_contracts(self):
        """Load Contracts From Storage."""
        # In A Real Implementation, This Would Load From Database
        pass

    def deploy_contract(self, code: bytes, owner: str, initial_state: Dict = None) -> str:
        """Deploy A New Smart Contract."""
        import time
        contract_id = sha256(code + owner.encode() + str(time.time()).encode()).hexdigest()[:16]
        contract = SmartContract(contract_id, code, owner, initial_state)
        contract.created_at = int(time.time())
        self.contracts[contract_id] = contract

        # Save To Storage
        storage.save_contract(contract.to_dict())
        logger.info(f"Deployed Contract {contract_id} By {owner}")
        return contract_id

    def call_contract(self, contract_id: str, method: str, params: List[Any],
                     caller: str, value: int = 0, gas_limit: int = 100000) -> Dict:
        """Call A Contract Method With Gas Limit."""
        contract = self.contracts.get(contract_id)
        if not contract:
            # Try To Load From Storage
            contract_data = storage.load_contract(contract_id)
            if contract_data:
                contract = SmartContract.from_dict(contract_data)
                self.contracts[contract_id] = contract
            else:
                return {'error': 'Contract Not Found', 'gas_used': 0}

        result = contract.execute(method, params, caller, value, gas_limit)
        if 'success' in result or 'result' in result:
            contract.updated_at = int(time.time())
            storage.save_contract(contract.to_dict())

        return result

    def get_contract(self, contract_id: str) -> Optional[SmartContract]:
        """Get A Contract By ID."""
        contract = self.contracts.get(contract_id)
        if not contract:
            contract_data = storage.load_contract(contract_id)
            if contract_data:
                contract = SmartContract.from_dict(contract_data)
                self.contracts[contract_id] = contract
        return contract


# Global Contract Manager
contract_manager = ContractManager()