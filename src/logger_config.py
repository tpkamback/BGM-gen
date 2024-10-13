import logging
import time
import os
from datetime import datetime

# set timezone
os.environ['TZ'] = 'Asia/Tokyo'
time.tzset()

# set log file
log_filename = datetime.now().strftime('%Y-%m%d-%H%M.log')
log_file = os.path.join(os.path.dirname(__file__), f'../log/{log_filename}')

def setup_logger(name=__name__):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # console handler (INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # file hundller (DEBUG)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
