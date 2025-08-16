#TODO
# Move some funcs from main to a logic.py module
# Make download funcs more modular, add params: bool - incl sigs, ..
# Improve MethodRequests class to use URLLIB for building urls. add skip= update
# make ServiceTicket store important data such as sig url
# add sig url download method to ServiceTicket
# Improve comments
# Improve logging
# Improve func sigs
# Add incl sigs checkbox to UI
# Improve autorun install script to not have cmd prompt open
# update requirements
# Improve pop up info windows
# add tests

import logging

import traceback

from datetime import date

from logic import perform_full_download
from config import SAVE_FOLDER_PATH, FILTER
from utils import load_config_json, update_config_json, initialize_storage_folder, initialize_config_json
from method_request import MethodRequest as mr

logger = logging.getLogger(__name__)
logging.basicConfig(filename='info.log',
                    level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

logger.debug(f"Imported the following variables-\nSAVE_FOLDER_PATH: "
             f"{SAVE_FOLDER_PATH}\nFILTER: {FILTER}")



def get_initialize_date():
    initialize_date = "2025-01-01"
    logger.info(f"INITIALIZING DATE: {initialize_date}")
    return initialize_date


def daily_download() -> None:
    last_scan = load_config_json("last_scan")
    if last_scan is None:
        last_scan = get_initialize_date()
    today = date.today().isoformat()

    daily_request = mr.get_request_by_range(start_date=today, end_date=last_scan, skip_amount=wo_total)
    perform_full_download(request_type=daily_request, wo_filter=FILTER)
    update_config_json(param="last_scan", new_value=date.today().isoformat())


if __name__ == '__main__':
    try:
        initialize_config_json()
        initialize_storage_folder()
        daily_download()
    except Exception as e:
        logger.error(f"Main function encountered an error: {traceback.format_exc()}")

