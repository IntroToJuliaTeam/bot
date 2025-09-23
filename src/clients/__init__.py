import os
from urllib.parse import urljoin

from dotenv import load_dotenv
from requests import Session


class LiveServerSession(Session):
    def __init__(self, base_url=None):
        super().__init__()
        self.base_url = base_url

    def request(self, method, url, *args, **kwargs):
        joined_url = urljoin(self.base_url, url)
        return super().request(method, joined_url, *args, **kwargs)


load_dotenv()

URL = os.environ["URL"]
PORT = os.environ["PORT"]

API_CLIENT = LiveServerSession(f"{URL}:{PORT}")

try:
    from src.gpt import RagClient, YandexGPTBot, YandexGPTConfig, prepare_index

    SERVICE_ACCOUNT_ID = os.environ["ACCOUNT_ID"]
    KEY_ID = os.environ["KEY_ID"]
    PRIVATE_KEY = os.environ["PRIVATE_KEY"].replace("\\n", "\n")
    FOLDER_ID = os.environ["FOLDER_ID"]
    TELEGRAM_TOKEN = os.environ["BOT_TOKEN"]

    s3_cfg = {
        "endpoint": os.environ["S3_ENDPOINT"],
        "access_key": os.environ["S3_ACCESS_KEY"],
        "secret_key": os.environ["S3_SECRET_KEY"],
        "bucket": os.environ["S3_BUCKET"],
        "prefix": os.environ.get("S3_PREFIX", ""),
    }

    GLOBAL_VECTOR_STORE = prepare_index(s3_cfg)
    RAG_CLIENT = RagClient()
    GPT_CLIENT = YandexGPTBot(
        YandexGPTConfig(SERVICE_ACCOUNT_ID, KEY_ID, PRIVATE_KEY, FOLDER_ID)
    )
except (ModuleNotFoundError, ImportError, KeyError) as e:
    print(e)
    GLOBAL_VECTOR_STORE = None
    RAG_CLIENT = None
    GPT_CLIENT = None
