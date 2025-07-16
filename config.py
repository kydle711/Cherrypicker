import os
from pathlib import Path
from dotenv import load_dotenv


URL = "https://rest.method.me/api/v1"
ROOT_FOLDER = 'pm-checklists'

load_dotenv(Path(__file__).with_name('.env'))

API_KEY = os.getenv("MY_API_KEY")

if not API_KEY:
    raise RuntimeError("MY_API_KEY could not be found")