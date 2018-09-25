
import os
import logging


log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

log_dir_path = os.path.dirname(os.path.realpath(__file__))
log_dir_path += "/logs"

try:
    os.makedirs(log_dir_path)
except os.error as err:
    # It's OK if the log directory exists. This is to be compatible with Python 2.7
    if err.errno != os.errno.EEXIST:
        raise err

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(console_handler)

from logging.handlers import RotatingFileHandler
rotating_log_handler = RotatingFileHandler(os.path.join(log_dir_path, "pydmcharting.log"), maxBytes=2000000,
                                           backupCount=100)
rotating_log_handler.setFormatter(log_formatter)
logger.addHandler(rotating_log_handler)
