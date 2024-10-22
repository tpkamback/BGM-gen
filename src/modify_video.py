from pydub import AudioSegment
import glob
import os
import re
import shutil

from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
from collections import defaultdict

from logger_config import setup_logger

logger = setup_logger(__name__)

# 1MBをバイト単位で表す定数
BYTES_IN_MB = 1024 * 1024

def get_inputs_files(directory):
    mp3_files = glob.glob(os.path.join(directory, "*.mp3"))
    img_files = glob.glob(os.path.join(directory, "*.[jp][pn]g"))

    filename = os.path.basename(mp3_files[0])
    prompt = re.sub(r"\(\d+\)\.mp3$", "", filename).strip()

    logger.debug(f"MP3 files found: {mp3_files}")
    logger.info(f"MP3 files(num={len(mp3_files)}) found")
    logger.info(f"IMG files found: {img_files}")
    logger.info(f"{prompt=}")

    return mp3_files, img_files, prompt

def get_mp3files_from_download(directory):
    mp3_files = glob.glob(os.path.join(directory, "*.mp3"))

    grouped_files = defaultdict(list)
    for file in mp3_files:
        filename = os.path.basename(file)
        
        if not filename.startswith("[suno]"):
            continue

        prompt = filename.replace("[suno]", "").replace(".mp3", "").strip()
        prompt = re.sub(r'\s*\(\d+\)', '', prompt)

        grouped_files[prompt].append(file)

    logger.debug(f"MP3 files found: {grouped_files}")

    return grouped_files

def move_files(files, output_dir):
    def move_file(file, output_dir):
        logger.debug(f"file: {file}")
        after_name = os.path.join(output_dir, os.path.basename(file))
        shutil.move(file, after_name)
        logger.debug(f"files renamed: {after_name}")

    if isinstance(files, list):
        for file in files:
            move_file(file, output_dir)
    else:
        move_file(files, output_dir)

def get_thumbnail_files(directory):
    png_files = glob.glob(os.path.join(directory, "*.png"))

    ret = []
    for file in png_files:
        filename = os.path.basename(file)
        
        if filename.startswith("used_"):
            continue

        ret.append(file)


    logger.debug(f"thumbnail_file : {ret=}")

    return ret

def merge_mp3(mp3_files, output_file):
    combined = AudioSegment.empty()
    for mp3_file in mp3_files:
        logger.info(f"Merging MP3 file: {mp3_file}")
        try:
            audio = AudioSegment.from_mp3(mp3_file)
        except Exception as e:
            logger.warning(f"continue to next video because error occured! : {e=}")
            continue

        combined += audio

    combined.export(output_file, format="mp3")

def create_text_image(text, image_file, text_img_path = "text_image.png" , max_font_size=200, font_path="/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"):
    # 元の画像のサイズを取得
    size = Image.open(image_file).size

    # テキストが画像内に収まるまでフォントサイズを調整
    font_size = max_font_size
    while font_size > 10:  # 最小フォントサイズを10に制限
        text_img = Image.new('RGBA', size, color=(0, 0, 0, 0))  # 透明な背景の画像
        draw = ImageDraw.Draw(text_img)
        font = ImageFont.truetype(font_path, font_size)

        # テキストのバウンディングボックスを取得
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

        # テキストが画像に収まるかどうかチェック
        if text_width <= size[0] and text_height <= size[1]:
            break  # フォントサイズが適切ならループを抜ける
        font_size -= 5  # フォントサイズを少しずつ小さくする

    # テキストを中央に配置
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    draw.text(position, text, font=font, fill="white")

    # テキスト画像を一時ファイルに保存
    text_img.save(text_img_path)
    
    return text_img_path

def compress_image(input_path, max_size_mb=2, quality=95):
    img = Image.open(input_path)
    orig_size = os.path.getsize(input_path) / BYTES_IN_MB  # MB単位に変換
    logger.debug(f"Original size: {orig_size:.2f} MB")
    
    while orig_size > max_size_mb:
        # 入力ファイルを直接上書き保存
        img.save(input_path, "JPEG", quality=quality)
        
        # 新しいファイルサイズを確認
        new_size = os.path.getsize(input_path) / BYTES_IN_MB
        logger.debug(f"Compressed size: {new_size:.2f} MB with quality: {quality}")
        
        # サイズが制限以下になったら終了
        if new_size <= max_size_mb:
            break
        
        # 品質を下げる
        quality = max(quality - 5, 10)

    return input_path

def create_video(mp3_files, audio_file, image_file, output_file, text_img_path, thumbnail_output, text="サムネの文字"):
    logger.debug(f"Merging audio file: {audio_file}")
    merge_mp3(mp3_files, audio_file)

    logger.debug(f"Loading audio file: {audio_file}")
    audio = AudioFileClip(audio_file)
    
    logger.debug(f"Loading image file: {image_file}")
    image_clip = ImageClip(image_file).set_duration(audio.duration)
    
    logger.debug("Adding fade-in effect to the image")
    image_clip = image_clip.set_audio(audio)  # 画像は最初から表示される
    
    # Pillowを使ってテキスト画像を作成し、ImageClipとして読み込む
    logger.debug(f"Adding text: {text}")
    text_image_file = create_text_image(text, image_file, text_img_path)
    
    # テキストクリップをフェードイン・フェードアウトで設定
    text_clip = ImageClip(text_image_file).set_duration(5).fadein(1).fadeout(1)
    text_clip = text_clip.set_position('center')
    
    # 画像クリップとテキストクリップを合成
    logger.debug("Combining image and text into video")
    video = CompositeVideoClip([image_clip, text_clip])
    
    # サムネイル用の画像を保存 (例えばフェードイン後1秒の時点)
    thumbnail_time = 2  # フェードインが完了した後の1秒目あたりをサムネイルとしてキャプチャ
    logger.debug(f"Saving thumbnail at {thumbnail_time} seconds")
    frame = video.get_frame(thumbnail_time)  # 特定の時間でフレームを取得
    thumbnail_image = Image.fromarray(frame)
    thumbnail_image.save(thumbnail_output)
    max_size_mb = 2
    
    if os.path.getsize(thumbnail_output) / BYTES_IN_MB > max_size_mb:
        logger.warning(f"Image file size exceeds {max_size_mb}MB. Compressing...")
        thumbnail_output = compress_image(thumbnail_output, max_size_mb)
    
    logger.debug(f"Thumbnail saved to {thumbnail_output}")
    
    logger.debug(f"Exporting video to {output_file}")
    video.write_videofile(
        output_file,
        fps=10,                     # 静止画なのでFPSを低めに設定
        codec='libx264',             # エンコーダ
        preset='fast',               # エンコード速度を高速に
        threads=4,                   # 並列処理でCPUリソースを最大限に活用
        bitrate="500k"               # ビットレートを下げてエンコード速度を向上
    )

    logger.debug(f"Video created: {output_file}")
