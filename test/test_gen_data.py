import requests
import unittest
from unittest.mock import patch, MagicMock
from gen_data import get_discprt_from_gpt, create_localizations

class TestGetDiscprtFromGpt(unittest.TestCase):
    
    @patch('requests.post')
    def test_get_discprt_from_gpt_normal(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": 'title="Calm Piano Melody"\n\ndisc= Immerse yourself...'
                    }
                }
            ]
        }
        
        prompt = "Describe a calming piano music."
        title, disc = get_discprt_from_gpt(prompt)
        
        self.assertEqual(title, "Lofi x Classic Calm Piano Melody")
        self.assertEqual(disc, "Immerse yourself...")

    @patch('requests.post')
    def test_get_discprt_from_gpt_missing_fields(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": 'disc=This content lacks a title.'
                    }
                }
            ]
        }
        
        with self.assertRaises(ValueError) as context:
            get_discprt_from_gpt("Prompt that lacks title.")
        self.assertEqual(str(context.exception), "Both 'title=' and 'disc=' must be present in the content.")

    @patch('requests.post')
    def test_get_discprt_from_gpt_http_error(self, mock_post):
        mock_post.return_value = MagicMock(status_code=404)
        mock_post.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
        
        prompt = "Prompt for an error test."
        title, disc = get_discprt_from_gpt(prompt)
        
        self.assertEqual(title, "Lofi x Classic Ethereal Evening: A Serene Piano Nocturne")
        self.assertEqual(disc, "Immerse yourself in the tranquil sounds of this soothing piano nocturne. With its soft and flowing melodies, this piece creates a peaceful atmosphere perfect for relaxation, meditation, or winding down after a long day. Let the calm tones wash over you, providing a gentle escape into serenity.")


class TestLocalizationFunctions(unittest.TestCase):

    @patch('gen_data.deepl.Translator')
    def test_create_localizations(self, MockTranslator):
        mock_translator = MockTranslator.return_value
        
        mock_translator.translate_text.side_effect = [
            MagicMock(text='Translated Title in Spanish'),  # JA
            MagicMock(text='Translated Description in Spanish')  # JA
        ]

        title = "Original Title"
        description = "Original Description"
        languages = ["ES"]

        result = create_localizations(title, description, languages)

        expected_result = {
            "en": {
                "title": title,
                "description": description
            },
            "es": {
                "title": "Translated Title in Spanish",
                "description": "Translated Description in Spanish"
            }
        }

        self.assertEqual(result, expected_result)

if __name__ == "__main__":
    unittest.main()
