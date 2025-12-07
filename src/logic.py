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

def request_data(request_type: str, params: dict = None) -> list[dict] | None:
    """ This function handles making multiple attempts at the request if an error is encountered
    and logging any info from the request. It also loops continually until all records from a request
     are exhausted."""
    failed_attempts = 0
    data =[]
    skip = 0
    while failed_attempts < 3:
        params['skip'] = skip
        logger.debug(f"Request data - Attempt num: {failed_attempts}")
        logger.debug(f"Request params - {params}")
        response = requests.request("GET", request_type, params=params, headers=headers)
        if response.status_code == 200:
            logger.info(f"RESPONSE INFO {response.status_code} DATA RETURNED")
            response_data = json.loads(response.text)
            data.extend(flatten_data(response_data))
            if not 'nextLink' in response_data:
                break
            elif 'count' in response_data:
                skip += response_data['count']
        # too many requests error - wait for rolling time limit window to allow more
        elif response.status_code == 429:
            logger.info(f"TOO MANY REQUESTS {response.text}")
            sleep(60)
            failed_attempts += 1
        else:
            logger.info(f"Unknown Error! {response.text}")
            sleep(15)
            failed_attempts += 1
    if failed_attempts == 3:
        logger.debug(f"Exceeded 3 work orders request attempts. REQUEST TYPE: {request_type}")
    return data

def create_work_order_list(data: list[dict], wo_filter: str | None = None) -> list[WorkOrder]:
    """" This function handles creating and returning WorkOrder instances, whether a single work
    order dict is passed or a list of work orders is passed."""
    # Keys for the config needed to instantiate WorkOrders
    num, name, wo_type, sig_url = ('RecordID', 'EntityCompanyName', 'Comments', 'SignatureURL')
    work_order_list = []
    for item in data:
        if 'RecordID' in data:
            if wo_filter and wo_filter != item[wo_type]:
                continue
            try:
                wo_instance = WorkOrder(item[num], item[name], item[wo_type], data[sig_url])
                work_order_list.append(wo_instance)
            except Exception:
                logger.error(f"Work Order creation failed for: {item}"
                             f"with this error: {traceback.format_exc()}")
    logger.info(f"Created the following tickets: {work_order_list}")
    return work_order_list


def perform_full_download(request_type: str, params: dict=None, get_sigs=False, wo_filter=None) -> None:
    logger.debug(f"FULL DOWNLOAD REQUEST TYPE: {request_type}")
    download_total = 0
    work_order_data = request_data(request_type=request_type, params=params)
    logger.debug(f"Work order data: {work_order_data}")

    signature_list = load_config_json("SignatureList")
    wo_list = create_work_order_list(work_order_data, wo_filter=wo_filter)
    for wo in wo_list:
        download_total += wo.download_files()
        if get_sigs or wo.customer in signature_list:
            logger.debug(f"Downloading work order sig: {wo}")
            download_total += wo.download_signature()

    logger.info(f"Total work orders scanned: {len(work_order_data)}")
    logger.info(f"Files downloaded: {download_total}")

def _get_customer_names() -> list:
    names_list = []
    customers_request = mr.get_customer_names()
    params = mr.get_customer_name_params()
    logger.debug(f"Requesting names with following URL: {customers_request} and params: {params}")
    customer_data = request_data(request_type=customers_request, params=params)
    for customer in customer_data:
        logger.debug(customer)
    for customer in customer_data:
        if "CompanyName" in customer and customer["CompanyName"] != "":
            names_list.append(customer["CompanyName"])

    return names_list

def sync_customer_list():
    logger.info("Syncing customer list...")
    customer_names = _get_customer_names()
    logger.debug(f"Customer names: {customer_names}")
    customer_lookup_dict = {strip_customer_name(name): name for name in customer_names}
    update_config_json(param='customers', new_value=customer_lookup_dict)
