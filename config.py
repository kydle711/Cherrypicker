import os
from pathlib import Path
from dotenv import load_dotenv

URL = "https://rest.method.me/api/v1"
DOWNLOAD_URL = f"https://rest.method.me/api/v1"
SAVE_FOLDER_PATH = 'pm-checklists'

FILTER = 'PWD:PM'

file_id_request = f"{URL}/files?table=Activity&recordId="

load_dotenv(Path(__file__).with_name('.env'))

API_KEY = os.getenv("MY_API_KEY")

if not API_KEY:
    raise RuntimeError("MY_API_KEY could not be found")

headers = {'Authorization': f'APIKey {API_KEY}'}
payload = {}


strip_list = ['INVOICES',
              'REQ',
              'REQ\'D',
              'PO',
              'INV',
              'INVOICE',
              'IVNOICES',
              'I',
              'PREVIEW',
              'THEN',
              'EMAIL',
              'IN',
              'EMAI',
              'DO NOT SEND',
              '  '
              'CC',
              'RUN',
              'DO NOT',
              'READ',
              'NOTE',
              ' ',
              '-',
              ' ',
              '-',
              ' ',
              ' - ',
              ' -',
              '- ']