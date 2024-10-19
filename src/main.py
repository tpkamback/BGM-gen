import os
import logging

from gen_data import get_discprt_from_gpt, transrate, create_localizations
from modify_video import get_inputs_files, merge_mp3, create_video
from upload_video import upload
from logger_config import setup_logger

logger = setup_logger(__name__)

def main():
    input_dirs = ["./input", "./input2", "./input3", "./input4", "./input5"]
    output_dirs = ["./output", "./output2", "./output3", "./output4", "./output5"]
    for input_dir, output_dir in zip(input_dirs, output_dirs):
        print(f"{input_dir=}")
        print(f"{output_dir=}")

        merged_audio_file = os.path.join(output_dir, "merged_audio.mp3")
        video_output_file = os.path.join(output_dir, "output_video.mp4")
        thumbnail_output = os.path.join(output_dir, "thumbnail_output.png")
        text_img_path = os.path.join(output_dir, "text_img_path.png")
        title_text = "Lofi x Classic"
    
        mp3_files, img_files, prompt = get_inputs_files(input_dir)
        logger.info(f"Fetched MP3 files from directory: {input_dir}")

        title, description = get_discprt_from_gpt(prompt)
        logger.info(f"Got title, description.")

        localizations = create_localizations(title, description)
        logger.info(f"Created localizations.")

        logger.info(f"creating video ...")
        create_video(mp3_files, merged_audio_file, img_files[0], video_output_file, text_img_path, thumbnail_output, title_text)
        logger.info(f"created video : {video_output_file}")

        upload(title, description, video_output_file, thumbnail_output, localizations)
        logger.info(f"uploaded")

if __name__ == "__main__":
    main()