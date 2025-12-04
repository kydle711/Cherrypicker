import os
from pathlib import Path
from dotenv import load_dotenv

URL = "https://rest.method.me/api/v1"
DOWNLOAD_URL = f"https://rest.method.me/api/v1"
SAVE_FOLDER_PATH = 'C:/Users/fulle/Documents/pm-checklists'

CONFIG_FILE = '../config/config.json'
LOG_FILE = '../logs/app.log'

FILTER = 'PWD:PM'
SYNC_INTERVAL = 30

file_id_request = f"{URL}/files?table=Activity&recordId="

env_path = os.path.join(os.path.dirname(__file__), "..", "config", ".env")
load_dotenv(dotenv_path=os.path.abspath(env_path))

API_KEY = os.getenv("MY_API_KEY")

if not API_KEY:
    raise RuntimeError("MY_API_KEY could not be found")

headers = {'Authorization': f'APIKey {API_KEY}'}
payload = {}


strip_list = ['INVOICES',
              'REQ',
              'REQ\'D',
              'REQD',
              'REQUIRED',
              'RE-Q',
              'PO',
              'INV',
              'INVOICE',
              'IVNOICES',
              'INVOIC',
              'INVO',
              'INVOI',
              'INFORMATION',
              'AGAIN',
              'APPRV',
              'APPROVAL',
              'APPROV'
              '4',
              'CALL',
              'CALL4',
              ' FOR',
              ' I',
              'PREVIEW',
              'SIGNED',
              'WO',
              'HAVE',
              'SELL',
              'CREDIT',
              'CARD',
              'INFO',
              'ACH',
              'NEVER',
              ' TO',
              '/',
              'MUST',
              'MUS',
              'THEN',
              'EMAIL',
              'EMAILFOR',
              'NEED',
              ' TO',
              ' IN',
              'EMAI',
              'EMA',
              'DO NOT SEND',
              '  ',
              '&',
              '#',
              'RUN CC',
              'CC',
              ' C',
              ' CB',
              ' ON',
              'ONLY',
              'COD',
              'RUN',
              'DO NOT',
              'READ',
              'NOTE',
              '!!',
              ' ',
              '-',
              ' ',
              '-',
              ' ',
              ' - ',
              ' -',
              '- ']