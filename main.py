
import logging
import requests
import json

from time import sleep
from datetime import date

from config import SAVE_FOLDER_PATH, headers, FILTER
from utils import load_config_json, update_config_json, flatten_data, initialize_storage_folder
from service_ticket import ServiceTicket
from method_request import MethodRequest as mr

logger = logging.getLogger(__name__)
logging.basicConfig(filename='info.log',
                    level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

logger.debug(f"Imported the following variables-\nSAVE_FOLDER_PATH: "
             f"{SAVE_FOLDER_PATH}\nFILTER: {FILTER}")



def initialize_scan():
    logger.info("INITIALIZING SCAN")
    return "2025-01-01"


def request_work_orders(request_type: str) -> dict:
    attempts = 0
    while attempts < 3:
        logger.debug(f"Requesting work orders attempt num: {attempts}")
        response = requests.request("GET", request_type, headers=headers)
        if response.status_code == 200:
            logger.info(f"RESPONSE INFO {response.status_code} DATA RETURNED")
            sample_data = json.loads(response.text)
            return sample_data
        # too many requests error - wait for rolling window to allow more
        elif response.status_code == 429:
            logger.info(f"TOO MANY REQUESTS {response.text}")
            sleep(60)
            attempts += 1
        else:
            logger.info(f"Unknown Error! {response.text}")
            sleep(15)
            attempts += 1
    return None





def create_work_orders_list(raw_data, wo_filter: str | None = None) -> list[ServiceTicket]:
    # Keys for the data needed to instantiate WorkOrders
    num, name, wotype = ('RecordID', 'EntityCompanyName', 'Comments')
    data = flatten_data(raw_data)
    service_ticket_list = []
    if 'RecordID' in data:
        new_ticket = ServiceTicket(data[num], data[name], data[wotype])
        service_ticket_list.append(new_ticket)
        logger.info(f"Created the following tickets:\n{service_ticket_list}")
        return service_ticket_list

    if wo_filter:
        for item in data:
            if item[wotype] == wo_filter:
                try:
                    new_ticket = ServiceTicket(item[num], item[name], item[wotype])
                    service_ticket_list.append(new_ticket)
                except Exception as e:
                    logger.error(f"ServiceTicket creation failed for: {item}"
                                 f"with this error: {e}")
    else:
        for item in data:
            try:
                new_ticket = ServiceTicket(item[num], item[name], item[wotype])
                service_ticket_list.append(new_ticket)
            except Exception as e:
                logger.error(f"ServiceTicket creation failed for: {item}"
                             f"with this error: {e}")
    logger.info(f"Created the following tickets: {service_ticket_list}")
    return service_ticket_list


def perform_full_download(start: str, end: str) -> None:
    wo_list = []
    initialize_storage_folder()
    # Keep a tab of total tickets checked in the loop
    wo_total = 0
    download_total = 0
    while True:
        daily_work_orders = request_work_orders(
            mr.get_request_by_range(start_date=start, end_date=end, skip_amount=wo_total))

        for wo in create_work_orders_list(daily_work_orders, wo_filter=FILTER):
            wo_list.append(wo)
            download_total += wo.download_files()  # Returns num downloads

        """Keep count of work orders returned from create_work_orders_list(). If
         count is less than 100, there are no more tickets to request and loop can
         break. Else, keep looping and adding to wo_list"""
        if 'count' in daily_work_orders:
            wo_count = daily_work_orders['count']
        else:
            wo_count = 1

        wo_total += wo_count
        if wo_count < 100:
            break

    logger.info(f"Total work orders scanned: {wo_total}")
    logger.info(f"Num work orders added to download list: {len(wo_list)}")
    logger.info(f"Files downloaded: {download_total}")


def daily_download() -> None:
    last_scan = load_config_json("last_scan")
    if last_scan is None:
        last_scan = initialize_scan()
    today = date.today().isoformat()

    perform_full_download(start=last_scan, end=today)
    update_config_json(param="last_scan", new_value=date.today().isoformat())


if __name__ == '__main__':
    try:
        daily_download()
    except Exception as e:
        logger.error(f"Main function encountered an error: {e}")

