import logging
import time
import os

# タイムゾーンを日本時間 (JST) に設定
os.environ['TZ'] = 'Asia/Tokyo'
time.tzset()

# ログファイルのパスを指定
log_file = os.path.join(os.path.dirname(__file__), '../log/youtube_upload.log')

# ロギング設定
def setup_logger(name=__name__):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # フォーマッタの設定
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # コンソールハンドラ
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ファイルハンドラ
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)    # ファイルはDEBUGレベル
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
