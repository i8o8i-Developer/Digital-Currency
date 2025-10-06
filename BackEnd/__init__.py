# i8o8iCoin BackEnd Package

# Version Info
__version__ = "1.0.0"
__author__ = "i8o8iCoin DEVELOPER"

# Import Modules On Demand To Avoid Circular Dependencies
import importlib

def _import_module(name):
    """Import A Module By Name."""
    return importlib.import_module(f'.{name}', package=__name__)

# Define Available Modules
_AVAILABLE_MODULES = {
    'Config': 'Config',
    'Logger': 'logger',
    'Storage': 'Storage',
    'Crypto': 'Crypto',
    'Wallet': 'Wallet',
    'Transaction': 'Transaction',
    'BlockChain': 'BlockChain',
    'Consensus': 'Consensus',
    'SmartContract': 'SmartContract',
    'P2PNetwork': 'P2PNetwork',
    'P2PStr': 'P2PStr'
}

# Create Module Attributes On Demand
def __getattr__(name):
    if name in _AVAILABLE_MODULES:
        try:
            module = _import_module(_AVAILABLE_MODULES[name])
            # Cache The Module To Avoid Re-ImportingQ
            globals()[name] = module
            return module
        except ImportError as e:
            raise ImportError(f"Could Not Import {name}: {e}")
    raise AttributeError(f"module '{__name__}' Has No Attribute '{name}'")
