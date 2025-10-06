"""
Wallet.py
Simple Wallet: Create Keypairs, Addresses, And Sign Transactions.
"""
from .Crypto import gen_keypair, ecdsa_sign, schnorr_sign, sha256d
from . import Storage as storage


def create_wallet(name: str) -> dict:
    sk_hex, vk_hex = gen_keypair()
    addr = vk_hex  # Simplified Address (Pubkey Hex)
    storage.save_wallet(name, sk_hex, vk_hex, addr)
    return {'sk': sk_hex, 'vk': vk_hex, 'address': addr}


def get_wallet(name: str) -> dict:
    return storage.load_wallet(name)


def sign_message(wallet_name: str, message: bytes, scheme='ecdsa') -> dict:
    w = get_wallet(wallet_name)
    if not w:
        raise KeyError('Wallet Not Found')
    if scheme == 'ecdsa':
        sig = ecdsa_sign(w['sk'], message)
        return {'scheme': 'ecdsa', 'sig': sig}
    else:
        sig = schnorr_sign(w['sk'], message)
        return {'scheme': 'schnorr', 'sig': sig}


def get_balance(address_or_wallet_name: str) -> int:
    # Accept Either Address Or Wallet Name
    w = storage.load_wallet(address_or_wallet_name)
    if w:
        address = w['address']
    else:
        address = address_or_wallet_name
    utxos = storage.list_utxos(address)
    return sum(u['value'] for u in utxos)


def create_miner_account(name: str) -> dict:
    # Create A Wallet And Register As Miner
    w = create_wallet(name)
    storage.save_miner(name, w['address'])
    return {'name': name, 'address': w['address']}


# Ensure DB Exists
storage.init_db()