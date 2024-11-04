import os
import json
import requests
import time
import deepl

from config import Config
from logger_config import setup_logger

logger = setup_logger(__name__)

"""
reference doc
https://docs.aimlapi.com/api-overview/audio-models-music-and-vocal/suno-ai-v2/clip-generation/generate-with-gpt
"""


def sample(headers):
    response = requests.post(
        url="https://api.aimlapi.com/chat/completions",
        headers=headers,
        data=json.dumps(
            {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": "What kind of model are you?",
                    },
                ],
                "max_tokens": 512,
                "stream": False,
            }
        ),
    )
    response.raise_for_status()
    data = response.json()
    logger.info(f"{data=}")


def get_discprt_from_gpt(prompt, max_retries=10, wait_time_sec=60):
    api_key = os.getenv("AIML_API_KEY")
    logger.debug(f"AIML_API_KEY : {api_key=}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    url = "https://api.aimlapi.com/chat/completions"

    def requests_post(request, prompt, max_tokens=512):
        logger.debug(f"{request=}")
        return requests.post(
            url=url,
            headers=headers,
            data=json.dumps(
                {
                    "model": "gpt-4o",
                    "messages": [
                        {
                            "role": "user",
                            "content": f"{request} : {prompt}",
                        },
                    ],
                    "max_tokens": max_tokens,
                    "stream": False,
                }
            ),
        )

    def retries(response):
        for attempt in range(max_retries):
            try:
                response.raise_for_status()
                data = response.json()
                logger.debug(f"response : {data=}")
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(wait_time_sec)
                else:
                    logger.error("Max retries reached. Request failed.")
                    return None

    head = "Generate an appropriate Youtube "
    tail = " for the audio generated in the prompt below."

    request = head + "title" + tail
    response = requests_post(request, prompt, max_tokens=80)
    title = retries(response)

    request = head + "description" + tail
    response = requests_post(request, prompt)
    description = retries(response)

    # modify title
    logger.debug(f"original  : {title=}")
    if title is not None:
        title = Config.title + " : " + title
    if description is not None:
        description = Config.description + " : " + description

    logger.info(f"generated : {title=}")
    logger.info(f"generated : {description=}")

    return title, description


def bgm_gen_v1(headers):
    logger.warning("unsupported function!!")
    response = requests.post(
        url="https://api.aimlapi.com/generate",
        headers=headers,
        json={
            "prompt": "A story about frogs.",
            "make_instrumental": False,
            "wait_audio": False,
        },
    )
    logger.info(f"{response.content=}")
    # response.raise_for_status()
    # data = response.json()
    # logger.info(f"{data=}")


def bgm_gen_v2(headers):
    logger.warning("unsupported function!!")
    response = requests.post(
        url="https://api.aimlapi.com/v2/generate/audio/suno-ai/clip",
        headers=headers,
        json={"gpt_description_prompt": "A story about frogs."},
    )
    logger.info(f"{response.content=}")
    # response.raise_for_status()
    # data = response.json()
    # logger.info(f"{data=}")


def image_gen(headers, text):
    logger.warning("unsupported function!!")
    response = requests.post(
        "https://api.aimlapi.com/images/generations",
        headers=headers,
        json={
            "prompt": text,
            # "model" : "dall-e-3"
        },
    )
    data = response.json()
    logger.info(f"{data=}")


def image_gen_hugging_face(prompt):
    logger.warning("unsupported function!!")
    from diffusers import StableDiffusionPipeline

    # Hugging Faceのアクセストークン
    access_token = ""

    # モデルの読み込み
    pipe = StableDiffusionPipeline.from_pretrained(
        "CompVis/stable-diffusion-v1-4", use_auth_token=access_token
    )
    pipe = pipe.to("cpu")  # GPUが使用可能な場合はCUDAを使用

    # テキストプロンプトから画像生成
    prompt = "A beautiful landscape with mountains and rivers"
    image = pipe(prompt).images[0]

    # 画像を保存
    image.save("generated_image.png")


"""
https://developers.deepl.com/docs/ja/getting-started/your-first-api-request
"""


def transrate(text, languages=None, is_title=False):
    """
    与えられたテキストをDeepLで指定した言語に翻訳し、YouTubeのlocalization用言語コードに対応した翻訳結果を返す。
    """
    auth_key = os.getenv("DEEPL_API_KEY")
    logger.debug(f"DEEPL_API_KEY : {auth_key}")
    translator = deepl.Translator(auth_key)

    translations = {}
    for deepl_code, youtube_code in Config.deepl_to_youtube_lang_map.items():
        if (
            languages is None or deepl_code in languages
        ):  # languageがなければすべて実施 or 渡されたlanguagesに存在する言語のみ翻訳を行う
            try:
                if is_title and deepl_code == "JA":  # 日本語の時はtitle英語
                    translations[youtube_code] = text
                else:
                    result = translator.translate_text(text, target_lang=deepl_code)
                    translations[youtube_code] = (
                        result.text
                    )  # YouTubeのlocalizations形式に対応する言語コードで保存
            except deepl.DeepLException as e:
                logger.error(f"Error translating to {deepl_code}: {str(e)}")

    return translations


def create_localizations(title, description, languages=None):
    """
    GPTで取得したタイトルと説明をDeepLで翻訳し、LOCALIZATIONS形式で返す関数。
    """
    # デフォルト（英語）のタイトルと説明
    localizations = {"en": {"title": title, "description": description}}

    # 各言語に翻訳されたタイトルと説明を取得
    translated_titles = transrate(title, languages, is_title=True)
    translated_descriptions = transrate(description, languages, is_title=False)

    # LOCALIZATIONSの形式に追加
    for lang_code in translated_titles:
        localizations[lang_code] = {
            "title": translated_titles[lang_code],
            "description": translated_descriptions.get(
                lang_code, ""
            ),  # 翻訳がない場合のフォールバック処理
        }

    logger.debug(f"{localizations=}")

    return localizations


def main():
    api_key = os.getenv("AIML_API_KEY")
    logger.debug(f"{api_key=}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # sample(headers)

    title, dict = get_discprt_from_gpt(headers)

    # bgm_gen_v1(headers)
    # bgm_gen_v2(headers)

    # text = "Compose a Lo-fi track blending elements of classical music with mellow beats and ambient textures"
    # image_gen(headers, text)

    # image_gen_hugging_face(text)

    # transrate()


if __name__ == "__main__":
    main()
