import os
import pathlib
import dotenv


ROOT_DIR = pathlib.Path(__file__).parent.parent

dotenv.load_dotenv(ROOT_DIR / ".env")

BOT_TOKEN = os.environ.get("BOT_TOKEN")

API_ENDPOINT_URI = os.environ.get("API_ENDPOINT")
LOGGING_FORMAT = (
    "<level>{time:YYYY-MM-DD HH:mm:ss.SSS}</level> "
    "<level>{level}</level>: "
    "<level>{name}</level> - "
    "<level>{message}</level>"
)


REPORTS_FOLDER = ROOT_DIR / 'reports'
REPORTS_FOLDER.mkdir(exist_ok=True)
