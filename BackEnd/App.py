"""
App.py
Flask API That Exposes Wallet Creation, Balance, Send, and Simple Node Methods.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
from flasgger import Swagger
from marshmallow import Schema, fields, ValidationError
import asyncio
import sys
import os
import time
import hashlib
import jwt
import datetime
import secrets
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge

# Handle Imports For Both Direct Execution And Module Import
if __name__ == '__main__':
    # When Run Directly, Use Absolute Imports
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    from BackEnd.Wallet import create_wallet, get_wallet
    from BackEnd.BlockChain import Blockchain
    from BackEnd.P2PStr import PeerNetwork
    from BackEnd.P2PNetwork import p2p_network
    from BackEnd.Transaction import Transaction, TxInput, TxOutput
    from BackEnd import Storage as storage
    from BackEnd.Wallet import get_balance, create_miner_account
    from BackEnd.SmartContract import contract_manager
    from BackEnd.Consensus import consensus_engine, voting_system
    from BackEnd.Config import config
    from BackEnd.logger import logger
    from BackEnd import Wallet as wallet_module
else:
    # When Imported As Module, Use Relative Imports
    from .Wallet import create_wallet, get_wallet
    from .BlockChain import Blockchain
    from .P2PStr import PeerNetwork
    from .P2PNetwork import p2p_network
    from .Transaction import Transaction, TxInput, TxOutput
    from . import Storage as storage
    from .Wallet import get_balance, create_miner_account
    from .SmartContract import contract_manager
    from .Consensus import consensus_engine, voting_system
    from .Config import config
    from .logger import logger
    from . import Wallet as wallet_module


app = Flask(__name__)
CORS(app, origins=["*"], supports_credentials=True)
Swagger(app)

SECRET_KEY = secrets.token_hex(32)

# Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 Per Day", "50 Per Hour"]
)

# Prometheus Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Latency', ['method', 'endpoint'])
BLOCKCHAIN_HEIGHT = Gauge('blockchain_height', 'Current BlockChain Height')
MEMPOOL_SIZE = Gauge('mempool_size', 'Current Mempool Size')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Number Of Active Connections')

storage.init_db()
chain = Blockchain()
peers = PeerNetwork()


## JWT Auth Decorator
def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'ok': False, 'error': 'Missing Or Invalid Token'}), 401
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user = payload['username']
        except jwt.ExpiredSignatureError:
            return jsonify({'ok': False, 'error': 'Token Expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'ok': False, 'error': 'Invalid Token'}), 401
        return f(*args, **kwargs)
    return decorated


def api_key_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'ok': False, 'error': 'Missing API Key'}), 401

        valid_keys = config.get('api.api_keys', [])
        if api_key not in valid_keys:
            return jsonify({'ok': False, 'error': 'Invalid API Key'}), 401

        return f(*args, **kwargs)
    return decorated

def require_auth(f):
    """Combined Auth Decorator - Accepts Either JWT or API Key"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check For API Key First
        api_key = request.headers.get('X-API-Key')
        if api_key:
            valid_keys = config.get('api.api_keys', [])
            if api_key in valid_keys:
                request.auth_type = 'api_key'
                return f(*args, **kwargs)

        # Check For JWT
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                request.user = payload['username']
                request.auth_type = 'jwt'
                return f(*args, **kwargs)
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                pass

        return jsonify({'ok': False, 'error': 'Authentication required'}), 401
    return decorated

def metrics_collector(f):
    """Decorator To Collect Prometheus Metrics"""
    @wraps(f)
    def decorated(*args, **kwargs):
        start_time = time.time()
        method = request.method
        endpoint = request.path

        try:
            result = f(*args, **kwargs)
            status_code = result[1] if isinstance(result, tuple) else 200
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=str(status_code)).inc()
            REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(time.time() - start_time)
            return result
        except Exception as e:
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status='500').inc()
            REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(time.time() - start_time)
            raise e
    return decorated

@app.route('/contract/<contract_id>/events', methods=['GET'])
@jwt_required
def api_contract_events(contract_id):
    """Get contract event logs."""
    events = storage.get_contract_events(contract_id)
    return jsonify({'ok': True, 'events': events})

# Contract State Endpoint
@app.route('/contract/<contract_id>/state', methods=['GET'])
@jwt_required
def api_contract_state(contract_id):
    """Get contract state."""
    state = storage.get_contract_state(contract_id)
    return jsonify({'ok': True, 'state': state})

# Metrics Endpoint
@app.route('/metrics', methods=['GET'])
@metrics_collector
def metrics():
    """Prometheus-Style Metrics Endpoint."""
    # Update Gauges
    BLOCKCHAIN_HEIGHT.set(len(chain.chain))
    MEMPOOL_SIZE.set(len(chain.mempool))
    ACTIVE_CONNECTIONS.set(len(peers.peers))

    return prometheus_client.generate_latest(), 200, {'Content-Type': 'text/plain; charset=utf-8'}

# Simple In-Memory Miner Reward (now configurable)
MINING_REWARD = config.get('blockchain.mining_reward', 50)

# Input Validation Schemas
class WalletCreateSchema(Schema):
    name = fields.Str(required=False)

class TxSendSchema(Schema):
    from_ = fields.Str(required=True, data_key='from')
    to = fields.Str(required=True)
    amount = fields.Int(required=True)

class TxBatchSchema(Schema):
    transactions = fields.List(fields.Dict(), required=True)

class MinerSchema(Schema):
    name = fields.Str(required=True)

class ContractDeploySchema(Schema):
    code = fields.Str(required=True)
    owner = fields.Str(required=True)
    initial_state = fields.Dict(required=False)

class ContractCallSchema(Schema):
    method = fields.Str(required=True)
    params = fields.List(fields.Raw(), required=False)
    caller = fields.Str(required=True)
    value = fields.Int(required=False)
    gas_limit = fields.Int(required=False)

class TokenDeploySchema(Schema):
    name = fields.Str(required=True)
    symbol = fields.Str(required=True)
    decimals = fields.Int(required=False, load_default=18)
    total_supply = fields.Int(required=True)
    owner = fields.Str(required=True)

class StakingSchema(Schema):
    address = fields.Str(required=True)
    amount = fields.Int(required=True)

def validate_input(schema, data):
    try:
        return schema.load(data), None
    except ValidationError as err:
        return None, err.messages


@app.route('/wallet/create', methods=['POST'])
def api_create_wallet():
    data = request.json or {}
    valid, errors = validate_input(WalletCreateSchema(), data)
    if errors:
        return jsonify({'ok': False, 'error': errors}), 400
    name = valid.get('name') or f"wallet{int(time.time())}"
    w = create_wallet(name)
    return jsonify({'ok': True, 'wallet': w})

@app.route('/wallet/<name>', methods=['GET'])
def api_get_wallet(name):
    w = get_wallet(name)
    if not w:
        return jsonify({'ok': False, 'error': 'Not Found'}), 404
    
    # Get wallet balance
    balance = storage.get_wallet_balance(w['address'])
    
    # Add balance to wallet data
    w['balance'] = balance
    
    return jsonify({'ok': True, 'wallet': w})

@app.route('/tx/send', methods=['POST'])
@limiter.limit("10 per minute")
@require_auth
@metrics_collector
def api_send_tx():
    data = request.json or {}
    valid, errors = validate_input(TxSendSchema(), data)
    if errors:
        return jsonify({'ok': False, 'error': errors}), 400
    sender = valid['from_']
    to = valid['to']
    amount = valid['amount']
    wallet = get_wallet(sender)
    if not wallet:
        return jsonify({'ok': False, 'error': 'Sender Wallet Not Found'}), 404
    selected, total = storage.select_utxos_for_amount(wallet['address'], amount)
    if selected is None:
        return jsonify({'ok': False, 'error': 'Insufficient Funds'}), 400
    vin = [TxInput(s['txid'], s['vout']) for s in selected]
    change = total - amount
    vouts = [TxOutput(amount, to)]
    if change > 0:
        vouts.append(TxOutput(change, wallet['address']))
    tx = Transaction(vin, vouts)
    for idx, _ in enumerate(tx.vin):
        tx.sign_input(idx, sender, wallet_module)
    ok, reason = chain.submit_tx(tx)
    if not ok:
        return jsonify({'ok': False, 'error': reason}), 400
    p2p_network.broadcast('/receive/tx', {'tx': tx.to_dict()})
    return jsonify({'ok': True, 'tx': tx.to_dict()})

@app.route('/tx/batch', methods=['POST'])
@limiter.limit("5 Per Minute")
@require_auth
@metrics_collector
def api_batch_tx():
    """Send Multiple Transactions In A Single Request."""
    data = request.json or {}
    valid, errors = validate_input(TxBatchSchema(), data)
    if errors:
        return jsonify({'ok': False, 'error': errors}), 400

    transactions = valid['transactions']
    results = []

    for i, tx_data in enumerate(transactions):
        try:
            # Validate Individual Transaction
            tx_valid, tx_errors = validate_input(TxSendSchema(), tx_data)
            if tx_errors:
                results.append({'index': i, 'ok': False, 'error': tx_errors})
                continue

            sender = tx_valid['from_']
            to = tx_valid['to']
            amount = tx_valid['amount']

            wallet = get_wallet(sender)
            if not wallet:
                results.append({'index': i, 'ok': False, 'error': 'Sender Wallet Not Found'})
                continue

            selected, total = storage.select_utxos_for_amount(wallet['address'], amount)
            if selected is None:
                results.append({'index': i, 'ok': False, 'error': 'Insufficient Funds'})
                continue

            vin = [TxInput(s['txid'], s['vout']) for s in selected]
            change = total - amount
            vouts = [TxOutput(amount, to)]
            if change > 0:
                vouts.append(TxOutput(change, wallet['address']))

            tx = Transaction(vin, vouts)
            for idx, _ in enumerate(tx.vin):
                tx.sign_input(idx, sender, wallet_module)

            ok, reason = chain.submit_tx(tx)
            if ok:
                results.append({'index': i, 'ok': True, 'tx': tx.to_dict()})
            else:
                results.append({'index': i, 'ok': False, 'error': reason})

        except Exception as e:
            results.append({'index': i, 'ok': False, 'error': str(e)})

    # Broadcast All Successful Transactions
    successful_txs = [r['tx'] for r in results if r.get('ok') and 'tx' in r]
    if successful_txs:
        p2p_network.broadcast('/receive/batch_tx', {'transactions': successful_txs})

    return jsonify({'ok': True, 'results': results})

@app.route('/node/peers', methods=['GET','POST'])
def api_peers():
    if request.method == 'POST': 
        data = request.json or {}
        url = data.get('url')
        if url:
            p2p_network.add_peer(url)
            return jsonify({'ok': True})
        return jsonify({'ok': False, 'error': 'Missing URL'}), 400
    return jsonify({'peers': p2p_network.get_alive_peers()})

@app.route('/receive/tx', methods=['POST'])
def api_receive_tx():
    data = request.json or {}
    print('Received TX:', data)
    # Accept Tx Into Mempool If Valid
    txd = data.get('tx')
    try:
        # Rebuild Transaction
        vin = [TxInput(i['txid'], i['vout'], i.get('script_sig')) for i in txd.get('vin', [])]
        vout = [TxOutput(o['value'], o['address']) for o in txd.get('vout', [])]
        tx = Transaction(vin, vout)
        ok, reason = chain.submit_tx(tx)
        return jsonify({'ok': ok, 'reason': reason})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/miners', methods=['GET','POST'])
def api_miners():
    if request.method == 'POST':
        data = request.json or {}
        name = data.get('name')
        if not name:
            return jsonify({'ok': False, 'error': 'Missing Name'}), 400
        m = create_miner_account(name)
        return jsonify({'ok': True, 'miner': m})
    return jsonify({'miners': storage.list_miners()})


@app.route('/mining/prepare', methods=['POST'])
def api_prepare_mine():
    data = request.json or {}
    miner = data.get('miner')
    m = storage.get_miner(miner)
    if not m:
        return jsonify({'ok': False, 'error': 'Miner Not Found'}), 404
    txs = chain.prepare_block_for_miner(m['address'], reward=MINING_REWARD)
    return jsonify({'ok': True, 'txs': [t.to_dict() for t in txs]})


@app.route('/mining/mine', methods=['POST'])
@jwt_required
def api_mine():
    data = request.json or {}
    miner = data.get('miner')
    m = storage.get_miner(miner)
    if not m:
        return jsonify({'ok': False, 'error': 'Miner Not Found'}), 404
    if consensus_engine.algorithm in ['pos', 'dpos']:
        expected_producer = consensus_engine.select_block_producer()
        if expected_producer and expected_producer != m['address']:
            return jsonify({'ok': False, 'error': f'Not Authorized To Produce Block. Expected: {expected_producer}'}), 403
    txs = chain.prepare_block_for_miner(m['address'], reward=MINING_REWARD)
    block = chain.mine_block(txs, m['address'])
    added = chain.add_block(block, m['address'])
    if not added:
        logger.warning(f"Failed To Add Mined Block {block.index}")
        return jsonify({'ok': False, 'error': 'Failed To Add Mined Block'}), 500
    reward = consensus_engine.get_block_reward(m['address'])
    storage.add_miner_earnings(miner, reward)
    storage.update_miner_last_mined(miner, block.timestamp)
    included = [t.txid() for t in txs]
    chain.clear_mempool(included)
    p2p_network.broadcast('/receive/block', {'block': block.to_dict()})
    logger.info(f"Miner {miner} Successfully Mined Block {block.index} With Reward {reward}")
    return jsonify({'ok': True, 'block': block.to_dict(), 'reward': reward})


# Smart Contract Endpoints
@app.route('/contract/deploy', methods=['POST'])
@limiter.limit("5 per minute")
@require_auth
@metrics_collector
def api_deploy_contract():
    data = request.json or {}
    valid, errors = validate_input(ContractDeploySchema(), data)
    if errors:
        return jsonify({'ok': False, 'error': errors}), 400
    code_hex = valid['code']
    owner = valid['owner']
    initial_state = valid.get('initial_state', {})
    try:
        code = bytes.fromhex(code_hex)
        contract_id = contract_manager.deploy_contract(code, owner, initial_state)
        logger.info(f"Deployed contract {contract_id} by {owner}")
        return jsonify({'ok': True, 'contract_id': contract_id})
    except Exception as e:
        logger.error(f"Contract Deployment Failed: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 400

@app.route('/token/deploy', methods=['POST'])
@limiter.limit("5 per minute")
@require_auth
@metrics_collector
def api_deploy_token():
    """Deploy an ERC-20 compatible token contract."""
    data = request.json or {}
    valid, errors = validate_input(TokenDeploySchema(), data)
    if errors:
        return jsonify({'ok': False, 'error': errors}), 400

    name = valid['name']
    symbol = valid['symbol']
    decimals = valid.get('decimals', 18)
    total_supply = valid['total_supply']
    owner = valid['owner']

    # Create initial state for ERC-20 token
    initial_state = {
        'name': name,
        'symbol': symbol,
        'decimals': decimals,
        'total_supply': total_supply,
        'balances': {owner: total_supply},
        'allowances': {}
    }

    # Use empty bytecode for token contracts (interpreted by our runtime)
    code = b''
    contract_id = contract_manager.deploy_contract(code, owner, initial_state)

    logger.info(f"Deployed ERC-20 token {name} ({symbol}) by {owner}")
    return jsonify({
        'ok': True,
        'contract_id': contract_id,
        'token': {
            'name': name,
            'symbol': symbol,
            'decimals': decimals,
            'total_supply': total_supply
        }
    })


@app.route('/staking/deposit', methods=['POST'])
@limiter.limit("10 per minute")
@require_auth
@metrics_collector
def api_stake_deposit():
    """Deposit tokens for staking."""
    data = request.json or {}
    valid, errors = validate_input(StakingSchema(), data)
    if errors:
        return jsonify({'ok': False, 'error': errors}), 400

    address = valid['address']
    amount = valid['amount']

    # Check balance
    balance = get_balance(address)
    if balance < amount:
        return jsonify({'ok': False, 'error': 'Insufficient balance'}), 400

    # Add to stake
    consensus_engine.update_stake(address, consensus_engine._get_stake(address) + amount)

    # Update user staking info
    storage.add_stake(address, amount)

    logger.info(f"Address {address} staked {amount} tokens")
    return jsonify({'ok': True, 'staked': amount})

@app.route('/staking/withdraw', methods=['POST'])
@limiter.limit("5 per minute")
@require_auth
@metrics_collector
def api_stake_withdraw():
    """Withdraw staked tokens."""
    data = request.json or {}
    valid, errors = validate_input(StakingSchema(), data)
    if errors:
        return jsonify({'ok': False, 'error': errors}), 400

    address = valid['address']
    amount = valid['amount']

    current_stake = consensus_engine._get_stake(address)
    if current_stake < amount:
        return jsonify({'ok': False, 'error': 'Insufficient stake'}), 400

    # Remove from stake
    consensus_engine.update_stake(address, current_stake - amount)

    # Update user staking info
    storage.remove_stake(address, amount)

    logger.info(f"Address {address} withdrew {amount} tokens from stake")
    return jsonify({'ok': True, 'withdrawn': amount})

@app.route('/staking/<address>', methods=['GET'])
@metrics_collector
def api_get_stake(address):
    """Get staking information for an address."""
    stake = consensus_engine._get_stake(address)
    rewards = storage.get_staking_rewards(address)
    return jsonify({
        'ok': True,
        'address': address,
        'stake': stake,
        'rewards': rewards
    })

@app.route('/staking/rewards/<address>', methods=['POST'])
@limiter.limit("10 per minute")
@require_auth
@metrics_collector
def api_claim_rewards(address):
    """Claim staking rewards."""
    rewards = storage.get_staking_rewards(address)
    if rewards <= 0:
        return jsonify({'ok': False, 'error': 'No rewards available'}), 400

    # Add rewards to balance (this would typically create a transaction)
    # For now, we'll just reset the rewards
    storage.claim_staking_rewards(address)

    logger.info(f"Address {address} claimed {rewards} staking rewards")
    return jsonify({'ok': True, 'claimed': rewards})


@app.route('/contract/<contract_id>/call', methods=['POST'])
@limiter.limit("20 Per Minute")
@require_auth
@metrics_collector
def api_call_contract(contract_id):
    data = request.json or {}
    valid, errors = validate_input(ContractCallSchema(), data)
    if errors:
        return jsonify({'ok': False, 'error': errors}), 400
    method = valid['method']
    params = valid.get('params', [])
    caller = valid['caller']
    value = valid.get('value', 0)
    gas_limit = valid.get('gas_limit', 100000)
    result = contract_manager.call_contract(contract_id, method, params, caller, value, gas_limit)
    return jsonify(result)
# Health Check Endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({'ok': True, 'status': 'healthy'})


@app.route('/contract/<contract_id>', methods=['GET'])
def api_get_contract(contract_id):
    contract = contract_manager.get_contract(contract_id)
    if not contract:
        return jsonify({'ok': False, 'error': 'Contract Not Found'}), 404

    return jsonify({'ok': True, 'contract': contract.to_dict()})


@app.route('/contracts', methods=['GET'])
def api_list_contracts():
    owner = request.args.get('owner')
    contracts = storage.list_contracts(owner)
    return jsonify({'ok': True, 'contracts': contracts})


# Consensus Management Endpoints
@app.route('/consensus', methods=['GET'])
def api_get_consensus():
    return jsonify({
        'ok': True,
        'algorithm': consensus_engine.algorithm,
        'difficulty': chain.difficulty,
        'validators': len(consensus_engine.validators),
        'delegates': consensus_engine.delegates
    })


@app.route('/consensus', methods=['POST'])
def api_set_consensus():
    data = request.json or {}
    algorithm = data.get('algorithm')

    if algorithm not in ['pow', 'pos', 'dpos']:
        return jsonify({'ok': False, 'error': 'Invalid Algorithm'}), 400

    try:
        consensus_engine.set_algorithm(algorithm)
        config.set('consensus.algorithm', algorithm)
        logger.info(f"Changed Consensus Algorithm To {algorithm}")
        return jsonify({'ok': True, 'algorithm': algorithm})
    except Exception as e:
        logger.error(f"Failed To Change Consensus: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/consensus/stake', methods=['POST'])
def api_update_stake():
    data = request.json or {}
    address = data.get('address')
    stake = data.get('stake', 0)

    if not address:
        return jsonify({'ok': False, 'error': 'Missing Address'}), 400

    consensus_engine.update_stake(address, stake)
    logger.info(f"Updated Stake For {address}: {stake}")
    return jsonify({'ok': True})


@app.route('/consensus/vote', methods=['POST'])
def api_vote():
    data = request.json or {}
    voter = data.get('voter')
    delegate = data.get('delegate')
    weight = data.get('weight', 1)

    if not voter or not delegate:
        return jsonify({'ok': False, 'error': 'Missing Voter or Delegate'}), 400

    voting_system.vote(voter, delegate, weight)
    logger.info(f"{voter} Voted For {delegate} With Weight {weight}")
    return jsonify({'ok': True})


# Configuration Endpoints
@app.route('/config', methods=['GET'])
def api_get_config():
    return jsonify({'ok': True, 'config': dict(config.config)})


@app.route('/config', methods=['POST'])
def api_set_config():
    data = request.json or {}
    for key, value in data.items():
        config.set(key, value)
    logger.info(f"Updated Configuration: {data}")
    return jsonify({'ok': True})


# Enhanced Wallet Endpoints
@app.route('/wallet/<name>/balance', methods=['GET'])
def api_get_balance(name):
    balance = get_balance(name)
    return jsonify({'ok': True, 'balance': balance})


@app.route('/wallets', methods=['GET'])
def api_list_wallets():
    wallets = storage.list_wallets()
    return jsonify({'ok': True, 'wallets': wallets})


# Enhanced Node Endpoints
@app.route('/node/status', methods=['GET'])
def api_node_status():
    network_stats = p2p_network.get_network_stats()
    return jsonify({
        'ok': True,
        'blockchain': {
            'height': len(chain.chain),
            'difficulty': chain.difficulty,
            'mempool_size': len(chain.mempool)
        },
        'network': network_stats,
        'consensus': {
            'algorithm': consensus_engine.algorithm,
            'validators': len(consensus_engine.validators),
            'delegates': len(consensus_engine.delegates)
        },
        'contracts': len(storage.list_contracts())
    })


# Authentication Endpoints
SECRET_KEY = config.get('api.jwt_secret_key', 'i8o8i_coin_secret_key_2024')  # In Production, Use Environment Variable

@app.route('/auth/register', methods=['POST'])
def api_register():
    data = request.json or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'ok': False, 'error': 'Missing Required Fields'}), 400

    # Check If User Already Exists
    existing = storage.get_user_by_username(username)
    if existing:
        return jsonify({'ok': False, 'error': 'Username Already Exists'}), 400

    existing_email = storage.get_user_by_email(email)
    if existing_email:
        return jsonify({'ok': False, 'error': 'Email Already Exists'}), 400

    # Hash Password
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    # Create User
    user = {
        'username': username,
        'email': email,
        'password_hash': password_hash,
        'created': datetime.datetime.utcnow().isoformat(),
        'wallets': [],
        'contracts': []
    }

    storage.save_user(user)
    logger.info(f"Registered New User: {username}")

    return jsonify({'ok': True, 'message': 'User Registered Successfully'})

@app.route('/auth/login', methods=['POST'])
def api_login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'ok': False, 'error': 'Missing Credentials'}), 400

    user = storage.get_user_by_username(username)
    if not user:
        return jsonify({'ok': False, 'error': 'Invalid Credentials'}), 401

    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if user['password_hash'] != password_hash:
        return jsonify({'ok': False, 'error': 'Invalid Credentials'}), 401

    # Generate JWT token
    token = jwt.encode({
        'username': user['username'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, SECRET_KEY, algorithm='HS256')

    # Return User Data Without Password
    user_data = {
        'username': user['username'],
        'email': user['email'],
        'created': user['created'],
        'wallets': user.get('wallets', []),
        'contracts': user.get('contracts', [])
    }

    return jsonify({'ok': True, 'user': user_data, 'token': token})

@app.route('/auth/profile', methods=['GET'])
def api_get_profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'ok': False, 'error': 'Missing Or Invalid Token'}), 401

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        username = payload['username']

        user = storage.get_user_by_username(username)
        if not user:
            return jsonify({'ok': False, 'error': 'User Not Found'}), 404

        user_data = {
            'username': user['username'],
            'email': user['email'],
            'created': user['created'],
            'wallets': user.get('wallets', []),
            'contracts': user.get('contracts', [])
        }

        return jsonify({'ok': True, 'user': user_data})
    except jwt.ExpiredSignatureError:
        return jsonify({'ok': False, 'error': 'Token Expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'ok': False, 'error': 'Invalid Token'}), 401


if __name__ == '__main__':
    logger.info("Starting i8o8iCoin API server")

    # Start P2P network
    p2p_network.start()

    try:
        app.run(
            debug=config.get('network.debug', True),
            host=config.get('network.host', '0.0.0.0'),
            port=config.get('network.port', 5000),
            use_reloader=False
        )
    finally:
        p2p_network.stop()

if __name__ == '__main__':
    # Initialize And Start The Application
    pass  