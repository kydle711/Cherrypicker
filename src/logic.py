import logging
import requests
import json
from time import sleep

from config import headers
from service_ticket import ServiceTicket
from method_request import MethodRequest as mr
from utils import flatten_data, strip_customer_name, update_config_json

logger = logging.getLogger(__name__)

def request_data(request_type: str) -> dict | None:
    """ This function handles making multiple attempts at the request if an error is encountered
    and logging any info from the request. """
    attempts = 0
    while attempts < 3:
        logger.debug(f"Attempt num: {attempts}")
        response = requests.request("GET", request_type, headers=headers)
        if response.status_code == 200:
            logger.info(f"RESPONSE INFO {response.status_code} DATA RETURNED")
            response_data = json.loads(response.text)
            return response_data
        # too many requests error - wait for rolling window to allow more
        elif response.status_code == 429:
            logger.info(f"TOO MANY REQUESTS {response.text}")
            sleep(60)
            attempts += 1
        else:
            logger.info(f"Unknown Error! {response.text}")
            sleep(15)
            attempts += 1
    logger.debug(f"Exceeded 3 work orders request attempts. REQUEST TYPE: {request_type}")
    return None

def create_work_orders_list(data, wo_filter: str | None = None) -> list[ServiceTicket]:
    # Keys for the data needed to instantiate WorkOrders
    num, name, wotype, sig_url = ('RecordID', 'EntityCompanyName', 'Comments', 'SignatureURL')
    service_ticket_list = []
    if 'RecordID' in data:
        new_ticket = ServiceTicket(data[num], data[name], data[wotype], data[sig_url])
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


def perform_full_download(request_type: str, get_sigs=False, wo_filter=None) -> None:
    wo_list = []
    # Keep a tab of total tickets checked in the loop
    wo_total = 0
    download_total = 0
    while True:
        work_orders = request_data(request_type=request_type)

        for wo in create_work_orders_list(work_orders, wo_filter=wo_filter):
            wo_list.append(wo)
            download_total += wo.download_files()  # Returns num downloads

        """Keep count of work orders returned from create_work_orders_list(). If
         count is less than 100, there are no more tickets to request and loop can
         break. Else, keep looping and adding to wo_list"""
        if 'count' in work_orders:
            wo_count = work_orders['count']
        else:
            wo_count = 1

        wo_total += wo_count
        if wo_count < 100:
            break

    logger.info(f"Total work orders scanned: {wo_total}")
    logger.info(f"Num work orders added to download list: {len(wo_list)}")
    logger.info(f"Files downloaded: {download_total}")

def _get_customer_names() -> list:
    names_list = []
    total = 0
    while True:
        customers_request = mr.get_customer_names(skip_amount=total)
        logger.debug(f"Requesting names with following URL: {customers_request}")
        customer_data = request_data(request_type=customers_request)
        if customer_data:
            logger.debug(f"JSON DATA: {customer_data}")

            for entity in flatten_data(customer_data):
                # Filter out blank customer fields
                if entity["CompanyName"] != "":
                    names_list.append(entity["CompanyName"])
            if "count" in customer_data and customer_data["count"] < 100:
                break
            else:
                total += customer_data['count']
                continue

    return names_list

def sync_customer_list():
    customer_names = _get_customer_names()
    customer_lookup_dict = {strip_customer_name(name): name for name in customer_names}
    update_config_json(param='customers', new_value=customer_lookup_dict)