# Contract Event and State Retrieval
def get_contract_events(contract_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM contract_events WHERE contract_id=?', (contract_id,))
    events = [dict(row) for row in cur.fetchall()]
    conn.close()
    return events

def get_contract_state(contract_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT state FROM contracts WHERE contract_id=?', (contract_id,))
    row = cur.fetchone()
    conn.close()
    return json.loads(row['state']) if row else {}
"""
Storage.py
Simple SQLite Storage For Wallets, Blocks, And UTXOs.
"""
import sqlite3
import json
import os
from pathlib import Path
from typing import Optional

DB_DIR = Path(__file__).parent / 'Data'
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / 'i8o8iCoin.db'
WALLET_JSON_PATH = DB_DIR / 'Wallets.json'


def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    # Wallets: name, sk, vk, address
    cur.execute('''
    CREATE TABLE IF NOT EXISTS wallets (
        name TEXT PRIMARY KEY,
        sk TEXT NOT NULL,
        vk TEXT NOT NULL,
        address TEXT NOT NULL
    )
    ''')
    # Blocks: index, hash, prev_hash, data (json), nonce, timestamp
    cur.execute('''
    CREATE TABLE IF NOT EXISTS blocks (
        idx INTEGER PRIMARY KEY,
        hash TEXT,
        prev_hash TEXT,
        data TEXT,
        nonce INTEGER,
        timestamp INTEGER
    )
    ''')
    # UTXOs: txid, vout, address, value
    cur.execute('''
    CREATE TABLE IF NOT EXISTS utxos (
        txid TEXT,
        vout INTEGER,
        address TEXT,
        value INTEGER,
        PRIMARY KEY (txid, vout)
    )
    ''')
    # Contracts: contract_id, code, owner, state, balance, created_at, updated_at
    cur.execute('''
    CREATE TABLE IF NOT EXISTS contracts (
        contract_id TEXT PRIMARY KEY,
        code TEXT NOT NULL,
        owner TEXT NOT NULL,
        state TEXT NOT NULL,
        balance INTEGER DEFAULT 0,
        created_at INTEGER,
        updated_at INTEGER
    )
    ''')
    # Miners: name, address, active, last_mined, earnings
    cur.execute('''
    CREATE TABLE IF NOT EXISTS miners (
        name TEXT PRIMARY KEY,
        address TEXT NOT NULL,
        active INTEGER DEFAULT 0,
        last_mined INTEGER,
        earnings INTEGER DEFAULT 0
    )
    ''')
    # Staking: address, amount, rewards, last_reward_time
    cur.execute('''
    CREATE TABLE IF NOT EXISTS staking (
        address TEXT PRIMARY KEY,
        amount INTEGER DEFAULT 0,
        rewards INTEGER DEFAULT 0,
        last_reward_time INTEGER
    )
    ''')
    conn.commit()
    conn.close()
    init_user_tables()  # Initialize User Tables


def _load_wallets_json():
    """Load wallets from JSON file."""
    if WALLET_JSON_PATH.exists():
        try:
            with open(WALLET_JSON_PATH, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def _save_wallets_json(wallets):
    """Save wallets to JSON file."""
    with open(WALLET_JSON_PATH, 'w') as f:
        json.dump(wallets, f, indent=2)


def save_wallet(name: str, sk: str, vk: str, address: str):
    # Save to SQLite
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('REPLACE INTO wallets(name, sk, vk, address) VALUES (?, ?, ?, ?)', (name, sk, vk, address))
    conn.commit()
    conn.close()
    
    # Save To JSON
    wallets = _load_wallets_json()
    wallets[name] = {'sk': sk, 'vk': vk, 'address': address}
    _save_wallets_json(wallets)


def load_wallet(name: str) -> Optional[dict]:
    # Try SQLite first
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT name, sk, vk, address FROM wallets WHERE name = ?', (name,))
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    
    # Fallback To JSON
    wallets = _load_wallets_json()
    wallet = wallets.get(name)
    if wallet:
        # Save To SQLite For Consistency
        save_wallet(name, wallet['sk'], wallet['vk'], wallet['address'])
        return {'name': name, **wallet}
    
    return None


def list_wallets():
    # Get Wallets From SQLite
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT name, address FROM wallets')
    sqlite_wallets = {row['name']: {'name': row['name'], 'address': row['address']} for row in cur.fetchall()}
    conn.close()
    
    # Get Wallets From JSON
    json_wallets = _load_wallets_json()
    json_wallet_list = [{'name': name, 'address': data['address']} for name, data in json_wallets.items()]
    
    # Combine And DeDuplicate
    all_wallets = list(sqlite_wallets.values())
    for wallet in json_wallet_list:
        if wallet['name'] not in sqlite_wallets:
            all_wallets.append(wallet)
    
    return all_wallets


def save_block(idx: int, h: str, prev_hash: str, data: str, nonce: int, timestamp: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('REPLACE INTO blocks(idx, hash, prev_hash, data, nonce, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
                (idx, h, prev_hash, data, nonce, timestamp))
    conn.commit()
    conn.close()


def load_block(idx: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM blocks WHERE idx = ?', (idx,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def add_utxo(txid: str, vout: int, address: str, value: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('REPLACE INTO utxos(txid, vout, address, value) VALUES (?, ?, ?, ?)', (txid, vout, address, value))
    conn.commit()
    conn.close()


def remove_utxo(txid: str, vout: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('DELETE FROM utxos WHERE txid = ? AND vout = ?', (txid, vout))
    conn.commit()
    conn.close()


def list_utxos(address: str = None):
    conn = get_conn()
    cur = conn.cursor()
    if address:
        cur.execute('SELECT txid, vout, address, value FROM utxos WHERE address = ?', (address,))
    else:
        cur.execute('SELECT txid, vout, address, value FROM utxos')
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_utxo(txid: str, vout: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT txid, vout, address, value FROM utxos WHERE txid = ? AND vout = ?', (txid, vout))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def select_utxos_for_amount(address: str, amount: int):
    """Greedy Selection: Returns List Of Utxos To Cover Amount And The Total Sum."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT txid, vout, address, value FROM utxos WHERE address = ? ORDER BY value DESC', (address,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    selected = []
    total = 0
    for r in rows:
        selected.append(r)
        total += r['value']
        if total >= amount:
            break
    if total < amount:
        return None, 0
    return selected, total


def save_miner(name: str, address: str, active: int = 1):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('REPLACE INTO miners(name, address, active) VALUES (?, ?, ?)', (name, address, active))
    conn.commit()
    conn.close()


def get_miner(name: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT name, address, active, last_mined, earnings FROM miners WHERE name = ?', (name,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def list_miners():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT name, address, active, last_mined, earnings FROM miners')
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def add_miner_earnings(name: str, amount: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('UPDATE miners SET earnings = COALESCE(earnings,0) + ? WHERE name = ?', (amount, name))
    conn.commit()
    conn.close()


def update_miner_last_mined(name: str, ts: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('UPDATE miners SET last_mined = ? WHERE name = ?', (ts, name))
    conn.commit()
    conn.close()


def save_contract(contract_data: dict):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
        REPLACE INTO contracts(contract_id, code, owner, state, balance, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        contract_data['contract_id'],
        contract_data['code'],
        contract_data['owner'],
        json.dumps(contract_data['state']),
        contract_data['balance'],
        contract_data['created_at'],
        contract_data['updated_at']
    ))
    conn.commit()
    conn.close()


def load_contract(contract_id: str) -> Optional[dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM contracts WHERE contract_id = ?', (contract_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    data = dict(row)
    data['state'] = json.loads(data['state'])
    return data


def list_contracts(owner: str = None):
    conn = get_conn()
    cur = conn.cursor()
    if owner:
        cur.execute('SELECT contract_id, owner, balance, created_at, updated_at FROM contracts WHERE owner = ?', (owner,))
    else:
        cur.execute('SELECT contract_id, owner, balance, created_at, updated_at FROM contracts')
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


# User Management Functions
def init_user_tables():
    conn = get_conn()
    cur = conn.cursor()
    # Users: username, email, password_hash, created, wallets, contracts
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created TEXT NOT NULL,
        wallets TEXT DEFAULT '[]',
        contracts TEXT DEFAULT '[]'
    )
    ''')
    conn.commit()
    conn.close()


def save_user(user: dict):
    init_user_tables()  # Ensure Table Exists
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
        INSERT OR REPLACE INTO users(username, email, password_hash, created, wallets, contracts)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        user['username'],
        user['email'],
        user['password_hash'],
        user['created'],
        json.dumps(user.get('wallets', [])),
        json.dumps(user.get('contracts', []))
    ))
    conn.commit()
    conn.close()


def get_user_by_username(username: str) -> Optional[dict]:
    init_user_tables()  # Ensure Table Exists
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE username = ?', (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    data = dict(row)
    data['wallets'] = json.loads(data['wallets'])
    data['contracts'] = json.loads(data['contracts'])
    return data


def get_user_by_email(email: str) -> Optional[dict]:
    init_user_tables()  # Ensure Table Exists
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE email = ?', (email,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    data = dict(row)
    data['wallets'] = json.loads(data['wallets'])
    data['contracts'] = json.loads(data['contracts'])
    return data


def update_user_wallets(username: str, wallets: list):
    init_user_tables()  # Ensure Table Exists
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('UPDATE users SET wallets = ? WHERE username = ?', (json.dumps(wallets), username))
    conn.commit()
    conn.close()


def update_user_contracts(username: str, contracts: list):
    init_user_tables()  # Ensure Table Exists
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('UPDATE users SET contracts = ? WHERE username = ?', (json.dumps(contracts), username))
    conn.commit()
    conn.close()


# Staking Functions
def add_stake(address: str, amount: int):
    """Add Stake For An Address."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO staking(address, amount, rewards, last_reward_time)
        VALUES (?, ?, 0, strftime('%s', 'now'))
        ON CONFLICT(address) DO UPDATE SET
        amount = amount + excluded.amount
    ''', (address, amount))
    conn.commit()
    conn.close()


def remove_stake(address: str, amount: int):
    """Remove Stake From An Address."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
        UPDATE staking SET amount = MAX(0, amount - ?) WHERE address = ?
    ''', (amount, address))
    conn.commit()
    conn.close()


def get_stake(address: str) -> int:
    """Get Stake Amount For An Address."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT amount FROM staking WHERE address = ?', (address,))
    row = cur.fetchone()
    conn.close()
    return row['amount'] if row else 0


def add_staking_rewards(address: str, amount: int):
    """Add Staking Rewards For An Address."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO staking(address, amount, rewards, last_reward_time)
        VALUES (?, 0, ?, strftime('%s', 'now'))
        ON CONFLICT(address) DO UPDATE SET
        rewards = rewards + excluded.rewards,
        last_reward_time = strftime('%s', 'now')
    ''', (address, amount))
    conn.commit()
    conn.close()


def get_staking_rewards(address: str) -> int:
    """Get Accumulated Staking Rewards For An Address."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT rewards FROM staking WHERE address = ?', (address,))
    row = cur.fetchone()
    conn.close()
    return row['rewards'] if row else 0


def claim_staking_rewards(address: str) -> int:
    """Claim Staking Rewards And Return The Amount Claimed."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT rewards FROM staking WHERE address = ?', (address,))
    row = cur.fetchone()
    if not row or row['rewards'] == 0:
        conn.close()
        return 0

    rewards = row['rewards']
    cur.execute('UPDATE staking SET rewards = 0 WHERE address = ?', (address,))
    conn.commit()
    conn.close()
    return rewards


def list_stakers():
    """Get All Addresses With Stakes."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT address, amount, rewards FROM staking WHERE amount > 0')
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows