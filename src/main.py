#TODO
# add sig url download method to WorkOrder
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
from app_config import SAVE_FOLDER_PATH, FILTER, LOG_FILE
from utils import load_config_json, update_config_json, initialize_storage_folder, initialize_config_json
from method_request import MethodRequest as mr

logger = logging.getLogger(__name__)
logging.basicConfig(filename=LOG_FILE,
                    level=logging.DEBUG,
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

    daily_request = mr.get_request_by_range(start_date=last_scan, end_date=today)
    perform_full_download(request_type=daily_request, wo_filter=FILTER)
    update_config_json(param="last_scan", new_value=today)


if __name__ == '__main__':
    config_flag = False
    try:
        initialize_config_json()
        initialize_storage_folder()
        config_flag = True
    except Exception as e1:
        logger.error(f"Main function encountered an error: {traceback.format_exc()}")

    if config_flag:
        try:
            daily_download()
        except Exception as e2:
            logger.error(f"Daily download failed: {traceback.format_exc()}")
    else:
        logger.error("DAILY DOWNLOAD DID NOT RUN DUE TO CONFIG ERROR")

