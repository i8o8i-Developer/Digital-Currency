"""
logger.py
Comprehensive Logging System For i8o8iCoin.
"""
import logging
import logging.handlers
import sys
from pathlib import Path

class Logger:
    def __init__(self):
        self.log_dir = Path(__file__).parent / 'logs'
        self.log_dir.mkdir(exist_ok=True)

        self.logger = logging.getLogger('i8o8iCoin')
        # Set default level, will be updated when config is available
        self.logger.setLevel(logging.INFO)

        # Remove Any Existing Handlers
        self.logger.handlers.clear()

        # Create Formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )

        # File Handler With Rotation (using defaults)
        log_file = self.log_dir / 'i8o8iCoin.log'
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # Try to update config-based settings
        self._update_from_config()

    def _update_from_config(self):
        """Update logger settings from config if available."""
        try:
            from .Config import config
            # Update log level
            level_name = config.get('logging.level', 'INFO')
            self.logger.setLevel(getattr(logging, level_name))

            # Update File Settings If Config Has Them
            if config.get('logging.file'):
                log_file = self.log_dir / config.get('logging.file')
                # Update Existing File Handler
                for handler in self.logger.handlers:
                    if isinstance(handler, logging.handlers.RotatingFileHandler):
                        handler.baseFilename = str(log_file)
                        handler.maxBytes = config.get('logging.max_file_size', 10485760)
                        handler.backupCount = config.get('logging.backup_count', 5)
                        break
        except ImportError:
            # Config Not Available Yet, Use Defaults
            pass
        except Exception as e:
            # Any Other Error, Log To Console
            print(f"Warning: Could Not Update Logger From Config: {e}")

    def get_logger(self, name=None):
        """Get A Logger Instance."""
        if name:
            return self.logger.getChild(name)
        return self.logger

# Global logger Instance
logger_instance = Logger()
logger = logger_instance.get_logger()