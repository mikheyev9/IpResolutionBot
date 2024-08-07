import os
import logging
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

class ColorFormatter(logging.Formatter):
    """Custom formatter to add colors to log levels."""
    COLORS = {
        logging.DEBUG: Style.DIM + Fore.CYAN,
        logging.INFO: Style.BRIGHT + Fore.GREEN,
        logging.WARNING: Style.BRIGHT + Fore.YELLOW,
        logging.ERROR: Style.BRIGHT + Fore.RED,
        logging.CRITICAL: Style.BRIGHT + Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        log_fmt = self.COLORS.get(record.levelno, '') + self._fmt + Style.RESET_ALL
        formatter = logging.Formatter(log_fmt, self.datefmt)
        return formatter.format(record)

logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('data/app.log')
file_handler.setLevel(logging.INFO)

formatter = ColorFormatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

file_formatter = logging.Formatter('%(asctime)s- %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)