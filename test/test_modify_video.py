import os
import hashlib
import shutil
import warnings
import pytest
import unittest
from modify_video import get_mp3files_from_download, get_thumbnail_files, create_video, move_files

@pytest.mark.parametrize("directory, expected", [
    ("./test/test_modify_video", {"test_gen_music": ["./test/test_modify_video/[suno]test_gen_music(1).mp3", "./test/test_modify_video/[suno]test_gen_music.mp3"]}),
])
def test_get_mp3files_from_download(directory, expected):
    grouped_files = get_mp3files_from_download(directory)
    assert grouped_files == expected

@pytest.mark.parametrize("directory, expected", [
    ("./test/test_modify_video",["./test/test_modify_video/test_thumbnail_0.png", "./test/test_modify_video/test_thumbnail_1.jpg"]),
])
def test_get_thumbnail_files(directory, expected):
    grouped_files = get_thumbnail_files(directory)
    assert grouped_files == expected

def calculate_file_hash(file_path):
    """ calculate SHA-256 hash value from specified file path"""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        hasher.update(f.read())

    return hasher.hexdigest()

class TestAPIRequest(unittest.TestCase):

    def setUp(self):
        warnings.filterwarnings(
            "ignore",
            category=DeprecationWarning,
            message="Starting with ImageIO v3 the behavior of this function will switch to that of iio.v3.imread"
        )

        self.output_dir = "./test/test_modify_video/output/"
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_api_request_success(self):
        mp3_files = ['./test/test_modify_video/[suno]test_gen_music(1).mp3', './test/test_modify_video/[suno]test_gen_music.mp3']
        thumbnail_file = "./test/test_modify_video/test_thumbnail_0.png"

        os.makedirs(self.output_dir, exist_ok=True)
        merged_audio_file = self.output_dir + "merged_audio.mp3"
        video_output_file = self.output_dir + "output_video.mp4"
        text_img_path = self.output_dir + "text_img_path.png"
        thumbnail_output = self.output_dir + "thumbnail_output.png"
        title_text = "Lofi x Classic"
        create_video(mp3_files, merged_audio_file, thumbnail_file, video_output_file, text_img_path, thumbnail_output, title_text)

        expected_dir = "./test/test_modify_video/expected"
        expected_hases = {f: calculate_file_hash(os.path.join(expected_dir, f)) for f in os.listdir(expected_dir)}
        output_hashes = {f: calculate_file_hash(os.path.join(self.output_dir, f)) for f in os.listdir(self.output_dir)}

        assert expected_hases == output_hashes

if __name__ == "__main__":
    unittest.main()
