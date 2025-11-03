"""
Config.py
Configuration Management For i8o8iCoin.
"""
import os
import json
from pathlib import Path

class Config:
    def __init__(self):
        self.config_dir = Path(__file__).parent / 'Config'
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / 'i8o8iCoin.json'
        self.defaults = {
            'network': {
                'port': 5000,
                'host': '0.0.0.0',
                'debug': True,
                'max_peers': 50,
                'peer_discovery_interval': 300,  # Seconds
                'heartbeat_interval': 60,  # Seconds
                'websocket_port': 5003,  # Changed To Avoid Any Lingering Port Conflicts
            },
            'blockchain': {
                'difficulty': 4,
                'block_time_target': 600,  # Seconds
                'max_block_size': 1000000,  # Bytes
                'max_tx_per_block': 1000,
                'mining_reward': 50,
                'halving_interval': 210000,  # Blocks
                'genesis_timestamp': 1609459200,  # 2021-01-01 00:00:00 UTC
            },
            'consensus': {
                'algorithm': 'pow',  # Pow, Pos, Dpos
                'pos_stake_minimum': 1000,
                'dpos_delegates': 21,
                'dpos_round_blocks': 21,
            },
            'crypto': {
                'signature_scheme': 'ecdsa',  # Ecdsa, Schnorr
                'hash_function': 'sha256',
                'address_version': '00',
            },
            'storage': {
                'db_path': 'Data/i8o8iCoin.db',
                'backup_interval': 3600,  # Seconds
                'max_db_size': 1000000000,  # 1GB
            },
            'api': {
                'rate_limit': 100,  # Requests Per Minute
                'cors_origins': ['*'],
                'auth_required': False,
                'api_keys': ['i8o8i_QSCVHIASLUGD2025T'],  
                'jwt_secret_key': 'i8o8i_2025COINASDFGHJKL',
                'session_timeout': 3600,  # 1 Hour
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/i8o8iCoin.log',
                'max_file_size': 10485760,  # 10MB
                'backup_count': 5,
            },
            'features': {
                'smart_contracts': True,
                'multi_sig': True,
                'timelocks': True,
                'privacy': False,
                'sidechains': False,
                'layer2': False,
            }
        }
        self.config = self.load_config()

    def load_config(self):
        """Load Configuration From File, Merging With Defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                return self._merge_configs(self.defaults, user_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could Not Load Config File: {e}")
                return self.defaults.copy()
        else:
            return self.defaults.copy()

    def _merge_configs(self, base, update):
        """Recursively Merge Configuration Dictionaries."""
        result = base.copy()
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result

    def save_config(self):
        """Save Current Configuration To File."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get(self, key_path, default=None):
        """Get Configuration Value By Dot-Separated Path."""
        keys = key_path.split('.')
        value = self.config
        try:
            for key in keys:
                value = value[key]
            return value
        except KeyError:
            return default

    def set(self, key_path, value):
        """Set Configuration Value By Dot-Separated Path."""
        keys = key_path.split('.')
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        self.save_config()

    def __getitem__(self, key):
        return self.config[key]

    def __setitem__(self, key, value):
        self.config[key] = value
        self.save_config()

# Global Configuration Instance
config = Config()