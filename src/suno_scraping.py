import os
import pickle
import logging
from typing import Dict, Any
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError


# from logger_config import setup_logger

# logger = setup_logger(__name__)

# YouTube Data APIのスコープ
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/youtube'
]

# 認証情報とトークンのパス
TOKEN_PATH = "./keys/token.pickle"
CLIENT_SECRETS_FILE = "./keys/client_secrets.json"

# 動画およびサムネイルのファイルパス
VIDEO_FILE = "./output/output_video.mp4"
THUMBNAIL_PATH = "./output/thumbnail_image.png"

# 動画のメタデータ
CATEGORY_ID = "10"  # 10 : Music
# PRIVACY_STATUS = "public"  # 'private', 'public', or 'unlisted'
PRIVACY_STATUS = "private"  # 'private', 'public', or 'unlisted'
MADE_FOR_KIDS = False  # 子供向けではない
TAGS = ["lofi", "chill music", "study beats"]
LICENSE_TYPE = "youtube"  # 標準ライセンス
EMBEDDABLE = True  # 埋め込み許可

from googleapiclient.discovery import build

def load_credentials() -> Any:
    """
    トークンファイルから認証情報を読み込む。
    存在しない場合や無効な場合は再認証を行う。
    """
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)
        logging.info("既存の認証トークンを読み込みました。")
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logging.info("認証トークンを更新しました。")
            except RefreshError:
                logging.error("トークンの更新に失敗しました。再認証が必要です。")
                creds = None
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server()
            logging.info("新しい認証トークンを取得しました。")
        
        # 認証情報を保存
        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)
            logging.info("認証トークンを保存しました。")
    
    return creds

print("a")
creds = load_credentials()
print("b")
youtube = build("youtube", "v3", credentials=creds)
print("c")

# 動画のlocalization情報を取得
video_id = 'oIPjdVY1-Hw'
# response = youtube.videos().list(
#     part='localizations',
#     id=video_id
# ).execute()


video_details = youtube.videos().list(
    part='snippet,localizations',
    id=video_id
).execute()

print(f"Current video details: {video_details}")

delete_localization_body = {
    'id': video_id,
    'localizations': None  # ローカライズ情報の削除を示す
}

response = youtube.videos().update(
    part='snippet',
    body=delete_localization_body
).execute()
print(f"{response=}")


print("dd")

update_localization_body = {
    'id': video_id,
    'snippet': {
        'title': '新しい日本語のタイトル',
        'description': '新しい日本語の説明',
        'categoryId': '10',
        'localizations': {
            'ja': {
                'title': '新しい日本語のタイトル',
                'description': '新しい日本語の説明'
            },
            'en': {
                'title': 'New English Title',
                'description': 'New English Description'
            }
        }
    }
}

# ローカライズ情報を更新するAPIリクエスト
response = youtube.videos().update(
    part='snippet',
    body=update_localization_body
).execute()
print(f"{response=}")

video_details = youtube.videos().list(
    part='snippet,localizations',
    id=video_id
).execute()
print("d")
print(f"{video_details=}")

# 結果を確認
localizations = response.get('items', [])[0].get('localizations', {})
print(localizations)
