# TODO
# Info/Error logging and output messages
# Run in background
# test on windows
# make another request when there are more than 100 tickets
# download multiple files?

import os
import shutil
import logging
import requests
import json
import urllib.request

from datetime import date, timedelta
from time import sleep

from config import API_KEY, ROOT_FOLDER, URL

skip_amount = 0
time_interval = 20

previous_day = "2025-6-4"
current_day = "2025-6-8"

file_id_request = f"{URL}/files?table=Activity&recordId="
work_order_info_request = f"{URL}/tables/Activity/"
headers = {'Authorization': f'APIKey {API_KEY}'}
payload = {}


class ServiceTicket:
    def __init__(self, record_id, customer, comments):
        self.work_order_num = record_id
        self.customer = customer
        self.comments = comments
        self.file_id = None
        self.file_ext = None
        self.save_file = None

        self._get_file_info()
        self._set_save_path()

    def __repr__(self):
        return (f"WORK ORDER NUMBER: {self.work_order_num}\n"
                f"CUSTOMER NAME: {self.customer}\n"
                f"WORK ORDER TYPE: {self.comments}\n"
                f"FILE ID: {self.file_id}\n\n")

    def _get_file_info(self):
        response = requests.request('GET', f"{file_id_request}{self.work_order_num}", headers=headers)
        try:
            self.file_id = json.loads(response.text)[0]['id']
            self.file_ext = json.loads(response.text)[0]['fileExtension']
        except IndexError or KeyError:
            self.file_id = None
            self.file_ext = None

    def _set_save_path(self):
        if self.file_ext is not None:
            self.save_file = f"{self.work_order_num}.{self.file_ext}"


def request_daily_work_orders() -> dict:
    attempts = 0
    print("Requesting daily work orders....")
    daily_completed_work_orders_request = (
        f"{URL}/tables/Activity?skip={skip_amount}&top=100&filter=ActualCompletedDate ge '{previous_day}T00:00:00' "
        f"and ActualCompletedDate lt '{current_day}T00:00:00'")

    while attempts < 3:
        response = requests.request("GET", daily_completed_work_orders_request, headers=headers)
        if response.status_code == 200:
            sample_data = json.loads(response.text)
            print("Done!")
            return sample_data
        elif response.status_code == 429:
            sleep(60)
            attempts += 1
            continue
        else:
            print("Unknown Error!")
            sleep(15)
            attempts += 1


def create_service_ticket_list(sample_data) -> list[ServiceTicket]:
    print("Creating service ticket list...")
    service_ticket_list = []
    for item in sample_data['value']:
        if item['Comments'] == 'PWD:PM':
            new_ticket = ServiceTicket(record_id=item['RecordID'],
                                       customer=item['EntityCompanyName'],
                                       comments=item['Comments'])
            service_ticket_list.append(new_ticket)
    print(f"Done!\n  {len(service_ticket_list)} tickets added to list.")
    return service_ticket_list


def download_checklists(work_order_list) -> None:
    print("Downloading files...")
    files_list = []
    for work_order in work_order_list:
        if work_order.file_id is not None:
            new_file_path = os.path.join(ROOT_FOLDER, work_order.customer, work_order.save_file)
            file_id = work_order.file_id
            url = f"https://rest.method.me/api/v1/files/{file_id}/download"
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)

            if response.status_code == 302:
                response_url = response.headers['Location']

                with urllib.request.urlopen(response_url) as resp, open(new_file_path, 'wb') as new_file:
                    shutil.copyfileobj(resp, new_file)
            files_list.append(work_order.save_file)
    print("Download complete")
    print(f"Downloaded the following {len(files_list)} files... {files_list}")


def initialize_storage_folder(parent_dir=ROOT_FOLDER) -> None:
    if not os.path.exists(parent_dir):
        print("Creating checklists folder...")
        os.mkdir(parent_dir)


def initialize_customer_folders(work_orders: list, parent_dir=ROOT_FOLDER) -> None:
    print("Creating customer folders...")
    new_folder_list = []
    for work_order in work_orders:
        if work_order.save_file:
            customer_dir_path = os.path.join(parent_dir, work_order.customer)
            if work_order.customer not in new_folder_list and not os.path.exists(customer_dir_path):
                os.mkdir(customer_dir_path)
                new_folder_list.append(work_order.customer)
    print(f"Done!\nAdded {len(new_folder_list)} new folders for the following customers...\n{new_folder_list}")


def set_today() -> str:
    today = date.today()
    date_string = f"{today.year}-{today.month}-{today.day}"
    return date_string


def set_yesterday() -> str:
    today = date.today()
    delta = timedelta(days=time_interval)
    yesterday = today - delta
    date_string = f"{yesterday.year}-{yesterday.month}-{yesterday.day}"
    return date_string


if __name__ == '__main__':
    ticket_list = []
    initialize_storage_folder()

    current_day = set_today()
    previous_day = set_yesterday()

    total_tickets = 0
    while True:
        ticket_count = 0
        daily_work_orders = request_daily_work_orders()

        for ticket in create_service_ticket_list(daily_work_orders):
            ticket_list.append(ticket)
        ticket_count = daily_work_orders['count']
        total_tickets += daily_work_orders['count']
        if ticket_count < 100:
            break
        else:
            skip_amount += ticket_count

    print(f"Retrieved {total_tickets} tickets")
    initialize_customer_folders(ticket_list)
    download_checklists(ticket_list)


