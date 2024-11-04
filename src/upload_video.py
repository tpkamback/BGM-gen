import os
import pickle
from typing import Dict, Any
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError


from logger_config import setup_logger

logger = setup_logger(__name__)

# YouTube Data APIのスコープ
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube",
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
DEFAULUT_LANGUAGE = "en"

YOUTUBE_API_TITLE_OVER_CAR = 100
YOUTUBE_API_DESCRIPTION_OVER_CAR = 5000

def load_credentials() -> Any:
    """
    トークンファイルから認証情報を読み込む。
    存在しない場合や無効な場合は再認証を行う。
    """
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)
        logger.info("既存の認証トークンを読み込みました。")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logger.info("認証トークンを更新しました。")
            except RefreshError:
                logger.error("トークンの更新に失敗しました。再認証が必要です。")
                creds = None
        if not creds:
            logger.warning("WSL/Docker環境未対応です。windowsで実行してください。")
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            creds = flow.run_local_server()
            logger.info("新しい認証トークンを取得しました。")

        # 認証情報を保存
        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)
            logger.info("認証トークンを保存しました。")

    return creds


def get_authenticated_service() -> Any:
    """
    認証済みのYouTubeサービスオブジェクトを取得する。
    """
    creds = load_credentials()
    youtube = build("youtube", "v3", credentials=creds)
    logger.info("YouTubeサービスオブジェクトを作成しました。")
    return youtube


def remove_char_limit_data(localizations):
    """Delete localizations that exceed the character limit."""
    logger.debug(f"{localizations=}")

    ret = {}
    for key, val in localizations.items():
        if "title" not in val:
            logger.warning(f"localization doesn't include title : {key} {val=}")
            continue
        if "description" not in val:
            logger.warning(f"localization doesn't include description : {key} {val=}")
            continue

        title = val["title"]
        description = val["description"]
        if len(title) >= YOUTUBE_API_TITLE_OVER_CAR:
            logger.warning(f"localization has over char : num={len(val)} : {key} {val=}")
            continue

        if len(description) >= YOUTUBE_API_DESCRIPTION_OVER_CAR:
            logger.warning(f"localization has over char : num={len(description)} : {key} {val=}")
            continue

        ret[key] = {
            "title" : title,
            "description" : description,
        }

    logger.debug(f"{ret=}")
    return ret


def upload_video(
    youtube: Any,
    file_path: str,
    title: str,
    description: str,
    category_id: str,
    privacy_status: str,
    made_for_kids: bool,
    tags: list,
    license_type: str,
    embeddable: bool,
    default_laguage: str,
    localizations: Dict[str, Dict[str, str]] = None,
) -> str:
    """
    YouTubeに動画をアップロードし、動画IDを返す。
    """
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id,
            "defaultLanguage": default_laguage,
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": made_for_kids,
            "license": license_type,
            "embeddable": embeddable,
        },
    }

    if localizations:
        body["localizations"] = remove_char_limit_data(localizations)

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    logger.debug(f"{body=}")
    logger.debug(f"{media=}")

    request = youtube.videos().insert(
        part="snippet,status,localizations", body=body, media_body=media
    )

    try:
        response = request.execute()
        video_id = response["id"]
        logger.info(f"Video uploaded successfully: {video_id}")
        logger.debug(f"{response=}")
        return video_id
    except Exception as e:
        logger.error(f"動画のアップロード中にエラーが発生しました: {e}")
        raise


def set_thumbnail(youtube: Any, video_id: str, thumbnail_path: str) -> None:
    """
    アップロードした動画にサムネイルを設定する。
    """
    logger.debug(f"{thumbnail_path=}")

    try:
        media = MediaFileUpload(thumbnail_path)
        request = youtube.thumbnails().set(videoId=video_id, media_body=media)
        request.execute()
        logger.info(f"Thumbnail set successfully for video: {video_id}")
    except Exception as e:
        logger.error(f"サムネイル設定中にエラーが発生しました: {e}")
        raise


def upload(title, description, file_path, thumbnail_output, localizations):
    """
    メイン関数。動画のアップロードとサムネイル設定を行う。
    """
    youtube = get_authenticated_service()

    try:
        # 動画アップロード
        video_id = upload_video(
            youtube=youtube,
            file_path=file_path,
            title=title,
            description=description,
            category_id=CATEGORY_ID,
            privacy_status=PRIVACY_STATUS,
            made_for_kids=MADE_FOR_KIDS,
            tags=TAGS,
            license_type=LICENSE_TYPE,
            embeddable=EMBEDDABLE,
            default_laguage=DEFAULUT_LANGUAGE,
            localizations=localizations,  # 多言語ローカライズを追加
        )

        # サムネイルの設定
        set_thumbnail(youtube, video_id, thumbnail_output)

    except Exception as e:
        logger.error(f"処理中にエラーが発生しました: {e}")
        raise

if __name__ == "__main__":
    load_credentials()
