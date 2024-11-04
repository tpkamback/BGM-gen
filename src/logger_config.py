import logging
import time
import os
import platform
from datetime import datetime

# set timezone
os.environ["TZ"] = "Asia/Tokyo"
if platform.system() != "Windows":
    time.tzset()

# set log file

now = datetime.now()
log_dirname = now.strftime("%Y-%m-%d")  # folder name : YYYY-MM-DD
log_filename = now.strftime("%H-%M-%S.log")  # file name : HH-MM-SS.log

output_dir = os.path.join(os.path.dirname(__file__), f"../log/{log_dirname}")
os.makedirs(output_dir, exist_ok=True)

log_file = os.path.join(output_dir, log_filename)


def setup_logger(name=__name__):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # console handler (INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # file hundller (DEBUG)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
