import unittest
from unittest.mock import patch, MagicMock
from gen_data import create_localizations


### [Todo] need to divide title, description loggic and test.
# class TestGetDiscprtFromGpt(unittest.TestCase):
#     @patch("requests.post")
#     def test_get_discprt_from_gpt_normal(self, mock_post):
#         mock_post.return_value = MagicMock(status_code=200)
#         mock_post.return_value.json.return_value = {
#             "choices": [
#                 {
#                     "message": {
#                         "content": 'title="Calm Piano Melody"\n\ndisc= Immerse yourself...'
#                     }
#                 }
#             ]
#         }

#         prompt = "Describe a calming piano music."
#         title, disc = get_discprt_from_gpt(prompt, max_retries=1, wait_time_sec=0)

#         self.assertEqual(title, Config.title + " : " + "Calm Piano Melody")
#         self.assertEqual(disc, Config.description + " : " + "Immerse yourself...")


class TestLocalizationFunctions(unittest.TestCase):
    @patch("gen_data.deepl.Translator")
    def test_create_localizations(self, MockTranslator):
        mock_translator = MockTranslator.return_value

        mock_translator.translate_text.side_effect = [
            MagicMock(text="Translated Title in Spanish"),  # JA
            MagicMock(text="Translated Description in Spanish"),  # JA
        ]

        title = "Original Title"
        description = "Original Description"
        languages = ["ES"]

        result = create_localizations(title, description, languages)

        expected_result = {
            "en": {"title": title, "description": description},
            "es": {
                "title": "Translated Title in Spanish",
                "description": "Translated Description in Spanish",
            },
        }

        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
