import logging
import requests
import json
import traceback

from time import sleep

from app_config import headers
from src.utils import load_config_json
from work_order import WorkOrder
from method_request import MethodRequest as mr
from utils import flatten_data, strip_customer_name, update_config_json

logger = logging.getLogger(__name__)

def request_data(request_type: str) -> dict | None:
    """ This function handles making multiple attempts at the request if an error is encountered
    and logging any info from the request. """
    attempts = 0
    while attempts < 3:
        logger.debug(f"Request data - Attempt num: {attempts}")
        response = requests.request("GET", request_type, headers=headers)
        if response.status_code == 200:
            logger.info(f"RESPONSE INFO {response.status_code} DATA RETURNED")
            response_data = json.loads(response.text)
            return response_data
        # too many requests error - wait for rolling time limit window to allow more
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

def create_work_order_list(data: dict, wo_filter: str | None = None) -> list[WorkOrder]:
    """" This function handles creating and returning WorkOrder instances, whether a single work
    order dict is passed or a list of work orders is passed."""
    # Keys for the config needed to instantiate WorkOrders
    num, name, wo_type, sig_url = ('RecordID', 'EntityCompanyName', 'Comments', 'SignatureURL')
    work_order_list = []
    # If data is a single work order instead of a dict of work orders, do this block
    if 'RecordID' in data:
        wo_object = WorkOrder(data[num], data[name], data[wo_type], data[sig_url])
        work_order_list.append(wo_object)
    # If a dict of multiple work orders, check for filter
    elif wo_filter:
        for item in data:
            if item[wo_type] == wo_filter:
                try:
                    wo_object = WorkOrder(item[num], item[name], item[wo_type], data[sig_url])
                    work_order_list.append(wo_object)
                except Exception as e:
                    logger.error(f"Work Order creation failed for: {item}"
                                 f"with this error: {traceback.format_exc()}")
    else:
        for item in data:
            try:
                wo_object = WorkOrder(item[num], item[name], item[wo_type], data[sig_url])
                work_order_list.append(wo_object)
            except Exception as e:
                logger.error(f"Work Order creation failed for: {item}"
                             f"with this error: {e}")
    logger.info(f"Created the following tickets: {work_order_list}")
    return work_order_list


def perform_full_download(request_type: str, get_sigs=False, wo_filter=None) -> None:
    logger.debug(f"FULL DOWNLOAD REQUEST TYPE: {request_type}")
    wo_list = []
    # Keep a tab of total tickets checked in the loop
    wo_total = 0
    download_total = 0
    while True:
        work_order_data = request_data(request_type=request_type)
        logger.debug(f"Work order data: {work_order_data}")

        """Keep count of work orders returned from create_work_orders_list(). If
         count is less than 100, there are no more tickets to request and loop can
         break. Else, keep looping and adding to wo_list"""
        if 'count' in work_order_data:
            wo_count = work_order_data['count']
            work_order_data = flatten_data(work_order_data)
        else:
            wo_count = 1

        for wo in create_work_order_list(work_order_data, wo_filter=wo_filter):
            logger.debug(f"WORK ORDER ADDED TO LIST: {wo}")
            wo_list.append(wo)
            # Returns num downloads and performs download
            download_total += wo.download_files()
            signature_list = load_config_json("SignatureList")
            if wo.customer in signature_list:
                wo.download_signature()

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
                # Filter out blank customer fields - unknown how this happens in method
                if entity["CompanyName"] != "":
                    names_list.append(entity["CompanyName"])
            if "count" in customer_data and customer_data["count"] < 100:
                break
            else:
                total += customer_data['count']
                continue

    return names_list

def sync_customer_list():
    logger.info("Syncing customer list...")
    customer_names = _get_customer_names()
    logger.debug(f"Customer names: {customer_names}")
    customer_lookup_dict = {strip_customer_name(name): name for name in customer_names}
    update_config_json(param='customers', new_value=customer_lookup_dict)
