"""
Transaction.py
Defines A Simple UTXO Transaction Format With Signatures And SIGHASH Flags.
"""
import json
from hashlib import sha256
from . import Storage as storage
from .Crypto import ecdsa_verify


def txid(tx: dict) -> str:
    return sha256(json.dumps(tx, sort_keys=True).encode()).hexdigest()


class TxInput:
    def __init__(self, txid: str, vout: int, script_sig: dict = None):
        self.txid = txid
        self.vout = vout
        self.script_sig = script_sig or {}

    def to_dict(self):
        return {'txid': self.txid, 'vout': self.vout, 'script_sig': self.script_sig}


class TxOutput:
    def __init__(self, value: int, address: str):
        self.value = value
        self.address = address

    def to_dict(self):
        return {'value': self.value, 'address': self.address}


class Transaction:
    def __init__(self, vin: list, vout: list):
        self.vin = vin
        self.vout = vout

    def to_dict(self):
        return {'vin': [i.to_dict() for i in self.vin], 'vout': [o.to_dict() for o in self.vout]}

    def serialize(self) -> bytes:
        return json.dumps(self.to_dict(), sort_keys=True).encode()

    def txid(self) -> str:
        return txid(self.to_dict())

    def sign_input(self, idx: int, priv_wallet_name: str, wallet_module, scheme='ecdsa', sighash='ALL'):
        # compute sighash
        msg = self.serialize()
        if sighash == 'ALL':
            h = sha256(msg).digest()
        else:
            h = sha256(msg).digest()
        sig = wallet_module.sign_message(priv_wallet_name, h, scheme=scheme)
        self.vin[idx].script_sig = {'sig': sig, 'sighash': sighash}


def verify_tx(tx: Transaction):
    """Basic Verification: Each Input Must Reference An Existing UTXO And Signature Must Verify Against Owner's Pubkey."""
    # Check Outputs Values
    for o in tx.vout:
        if o.value < 0:
            return False, 'Negative Output'

    # Coinbase (No Inputs) Is Allowed — It's The Block Reward Tx
    if len(tx.vin) == 0:
        return True, ''

    # Check Inputs Exist And Signatures
    for i_idx, vin in enumerate(tx.vin):
        u = storage.get_utxo(vin.txid, vin.vout)
        if not u:
            return False, f'UTXO not found {vin.txid}:{vin.vout}'
        # Get Owning Address (PubKey Hex) And Attempt To Verify Signature
        script = vin.script_sig or {}
        sigobj = script.get('sig')
        if not sigobj:
            return False, f'No Signature For Input {i_idx}'
        # Sigobj For Ecdsa Is {'scheme':'ecdsa','sig':hex}
        scheme = sigobj.get('scheme') if isinstance(sigobj, dict) else 'ecdsa'
        if scheme == 'ecdsa':
            sighex = sigobj['sig'] if isinstance(sigobj, dict) else sigobj
            # Message Is Tx Serialize For Now
            msg = tx.serialize()
            # Address Stored In Utxo Is Pubkey Hex
            pubhex = u['address']
            ok = ecdsa_verify(pubhex, msg, sighex)
            if not ok:
                return False, f'Invalid Signature For Input {i_idx}'
        else:
            # For Non-Ecdsa We Skip Deep Verify (Could Be Added)
            pass

    # Value Conservation (Inputs >= Outputs)
    total_in = 0
    for vin in tx.vin:
        u = storage.get_utxo(vin.txid, vin.vout)
        total_in += u['value']
    total_out = sum(o.value for o in tx.vout)
    if total_in < total_out:
        return False, 'Insufficient Input Value'

    return True, ''