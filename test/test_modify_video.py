import requests
import pytest
import unittest
from unittest.mock import patch, MagicMock
from modify_video import get_mp3files_from_download, get_thumbnail_files, create_video, move_files

@pytest.mark.parametrize("directory, expected", [
    ("./test/test_gen_data", {"test_gen_music": ["./test/test_gen_data/[suno]test_gen_music.mp3"]}),
])
def test_get_mp3files_from_download(directory, expected):
    grouped_files = get_mp3files_from_download(directory)
    assert grouped_files == expected

if __name__ == "__main__":
    unittest.main()
