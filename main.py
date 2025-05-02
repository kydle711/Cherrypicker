import os
import requests
import json

from datetime import date, timedelta

API_KEY = "NjdmNDY1ODUwZjFmMmQ3OGY2M2UzM2YwLjQ3RTZFQTg1Qzk0RDQ4QkM5MkVBQ0JGRDI1OEY5NUM2"
URL = "https://rest.method.me/api/v1"
ROOT_FOLDER = 'pm-checklists'

previous_day = ""
current_day = ""

skip_amount = 0

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

        self._set_file_id()

    def __repr__(self):
        return (f"WORK ORDER NUMBER: {self.work_order_num}\n"
                f"CUSTOMER NAME: {self.customer}\n"
                f"WORK ORDER TYPE: {self.comments}\n"
                f"FILE ID: {self.file_id}\n\n")

    def _set_file_id(self):
        response = requests.request('GET', f"{file_id_request}{self.work_order_num}", headers=headers)
        try:
            self.file_id = json.loads(response.text)[0]
        except IndexError:
            self.file_id = None


def request_daily_work_orders() -> dict:
    daily_completed_work_orders_request = (
        f"{URL}/tables/Activity?skip={skip_amount}&top=100&filter=ActualCompletedDate ge '{previous_day}T00:00:00' "
        f"and ActualCompletedDate lt '{current_day}T00:00:00'")

    print(daily_completed_work_orders_request)
    print("Requesting work orders...")
    response = requests.request("GET", daily_completed_work_orders_request, headers=headers)
    print(f"Response status code: {response.status_code}")
    sample_data = json.loads(response.text)
    return sample_data


def create_service_ticket_list(sample_data) -> list[ServiceTicket]:
    service_ticket_list = []
    for item in sample_data['value']:
        if item['Comments'] == 'PWD:PM':
            new_ticket = ServiceTicket(record_id=item['RecordID'],
                                       customer=item['EntityCompanyName'],
                                       comments=item['Comments'])
            service_ticket_list.append(new_ticket)
    return service_ticket_list


def download_checklists(work_order_list) -> None:
    print("Downloading files...")
    for work_order in work_order_list:
        if work_order.file_id is not None:
            file_id = work_order.file_id['id']
            url = f"https://rest.method.me/api/v1/files/{file_id}/download"
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=True)
            print(response.content)
            print(response.status_code)
            print(response.text)
            filename = f"{work_order.work_order_num}.{work_order.file_id['fileExtension']}"
            with open(os.path.join(ROOT_FOLDER, filename), 'wb') as file:
                file.write(response.content)

    print("Files successfully downloaded!")


def initialize_storage_folder(parent_dir=ROOT_FOLDER) -> None:
    if not os.path.exists(parent_dir):
        print("Creating checklists folder...")
        os.mkdir(parent_dir)


def initialize_customer_folders(work_orders: list[dict], parent_dir=ROOT_FOLDER) -> None:
    for work_order in work_orders:
        if not os.path.exists(work_order['Customer']):
            os.mkdir(os.path.join(parent_dir, work_order['Customer']))


def set_today() -> str:
    today = date.today()
    date_string = f"{today.year}-{today.month}-{today.day}"
    return date_string


def set_yesterday() -> str:
    today = date.today()
    delta = timedelta(days=1)
    yesterday = today - delta
    date_string = f"{yesterday.year}-{yesterday.month}-{yesterday.day}"
    return date_string


if __name__ == '__main__':
    initialize_storage_folder()

    current_day = set_today()
    previous_day = set_yesterday()

    daily_work_orders = request_daily_work_orders()

    ticket_list = create_service_ticket_list(daily_work_orders)

    for ticket in ticket_list:
        print(ticket)

    download_checklists(ticket_list)

    # initialize_customer_folders()
