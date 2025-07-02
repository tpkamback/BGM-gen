import os

from config import Config
from gen_data import get_discprt_from_gpt, create_localizations
from modify_video import (
    get_mp3files_from_download,
    get_thumbnail_files,
    create_video,
    move_files,
)
from upload_video import upload, load_credentials
from logger_config import setup_logger

logger = setup_logger(__name__)

USE_LOCALIZATION = False
USE_TITLE_DESC_GEN = False


def main():
    input_dir = "/downloads"
    thumbnail_dir = "/thumbnail"
    result_root_dir = "./result"

    # check if credentials is not expired.
    load_credentials()

    grouped_files = get_mp3files_from_download(input_dir)
    thumbnail_files = get_thumbnail_files(thumbnail_dir)

    for i, (prompt, mp3_files) in enumerate(grouped_files.items()):
        output_dir = os.path.join(result_root_dir, str(i))
        os.makedirs(output_dir, exist_ok=True)

        thumbnail_file = thumbnail_files.pop(0)

        logger.info(f"{input_dir=}")
        logger.info(f"{output_dir=}")
        logger.info(f"{prompt=}")
        logger.debug(f"{mp3_files=}")
        logger.debug(f"{thumbnail_file=}")

        merged_audio_file = os.path.join(output_dir, "merged_audio.mp3")
        video_output_file = os.path.join(output_dir, "output_video.mp4")
        thumbnail_output = os.path.join(output_dir, "thumbnail_output.png")
        text_img_path = os.path.join(output_dir, "text_img_path.png")
        title_text = Config.title

        if USE_TITLE_DESC_GEN:
            title, description = get_discprt_from_gpt(prompt)
            if title is None or description is None:
                logger.warning(
                    f"skip due to something happend : {title=} {description=}"
                )
                continue

            logger.info("Got title, description.")
        else:
            title = "test title"
            description = "test desc"
            logger.info(f"hand made title {title=}, {description=}.")

        localizations = None
        if USE_LOCALIZATION:
            localizations = create_localizations(title, description)
            logger.info("Created localizations.")

        logger.info("creating video ...")
        create_video(
            mp3_files,
            merged_audio_file,
            thumbnail_file,
            video_output_file,
            text_img_path,
            thumbnail_output,
            title_text,
        )
        logger.info(f"created video : {video_output_file}")

        upload(title, description, video_output_file, thumbnail_output, localizations)
        logger.info("uploaded")

        move_files(mp3_files, output_dir)
        move_files(thumbnail_file, output_dir)
        logger.info("file moved")


if __name__ == "__main__":
    main()
