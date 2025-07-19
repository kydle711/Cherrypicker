# TODO
# Info/Error logging and output messages
# Run in background
# download multiple files?
# Add GUI for manual downloads?

import os
import logging
import requests
import json

from time import sleep

from config import SAVE_FOLDER_PATH, headers, payload, FILTER
from service_ticket import ServiceTicket
from method_request import MethodRequest as mr

# 2 pics wo 30568
work_order_num_requested = 29199


def request_work_orders(request_type: str) -> dict:
    attempts = 0
    while attempts < 3:
        response = requests.request("GET", request_type, headers=headers)
        if response.status_code == 200:
            sample_data = json.loads(response.text)
            return sample_data
        # too many requests error - wait for rolling window to allow more
        elif response.status_code == 429:
            sleep(60)
            attempts += 1
        else:
            print(f"Unknown Error!  {response.status_code}, {response.text}")
            sleep(15)
            attempts += 1


def extract_values(sample_data):
    """Handles cases where the response contains multiple items with "count" and
    "value" keys or where it just contains a single value with no keys."""
    if 'value' in sample_data.keys():
        return sample_data['value']
    else:
        return sample_data


def create_work_orders_list(sample_data, filter: str | None = None) -> list[ServiceTicket]:
    data_values = extract_values(sample_data)
    requested_filter = filter
    service_ticket_list = []
    if filter:
        for item in data_values:
            if item['Comments'] == requested_filter:
                try:
                    new_ticket = ServiceTicket(record_id=item['RecordID'],
                                               customer=item['EntityCompanyName'],
                                               comments=item['Comments'])
                    service_ticket_list.append(new_ticket)
                except Exception as e:
                    print(Exception)
                    print(f"DOWNLOAD FAILED FOR THE FOLLOWING WORK ORDER:\n {item}")
    else:
        for item in data_values:
            new_ticket = ServiceTicket(record_id=item['RecordID'],
                                       customer=item['EntityCompanyName'],
                                       comments=item['Comments'])
            service_ticket_list.append(new_ticket)

    return service_ticket_list


def initialize_storage_folder(parent_dir=SAVE_FOLDER_PATH) -> None:
    if not os.path.exists(parent_dir):
        os.mkdir(parent_dir)


if __name__ == '__main__':
    wo_list = []
    initialize_storage_folder()

    # Keep a tab of total tickets checked in the loop
    wo_total = 0
    """while True:
        daily_work_orders = request_work_orders(mr.get_request_by_range(interval=30, skip_amount=total_tickets))

        for wo in create_work_orders_list(daily_work_orders, filter=FILTER):
            wo_list.append(wo)
        """"""Keep count of work orders returned from create_work_orders_list(). If
         count is less than 100, there are no more tickets to request and loop can
         break. Else, keep looping and adding to wo_list""""""
        wo_count = daily_work_orders['count']
        wo_total += wo_count
        if wo_count < 100:
            break"""

    test_wo = request_work_orders(mr.get_request_by_num(num_requested=30153))
    print(test_wo)
    wo_list.append(create_work_orders_list(test_wo))
    for wo in wo_list:
        wo.download_files()

    print(f"TOTAL TICKETS CHECKED: {wo_total}")
    print(f"TOTAL TICKETS ADDED TO DOWNLOAD LIST: {len(wo_list)}")
    print(f"TOTAL DOWNLOADS: {None}")