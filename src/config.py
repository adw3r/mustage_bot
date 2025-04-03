import os
import pathlib
import dotenv


ROOT_DIR = pathlib.Path(__file__).parent.parent

dotenv.load_dotenv(ROOT_DIR / ".env")

BOT_TOKEN = os.environ.get("BOT_TOKEN")

API_ENDPOINT_URI = os.environ.get("API_ENDPOINT")