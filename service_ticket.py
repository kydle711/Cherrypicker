import json
import requests
import os
import shutil
import urllib.request
import logging

from file_object import FileObject

from config import file_id_request, headers, strip_list, SAVE_FOLDER_PATH, URL, payload

logger = logging.getLogger(__name__)

logger.debug(f"Imported from config: \nfile_id_request: {file_id_request}\n"
             f"headers: {headers}\nSAVE_FOLDER_PATH: {SAVE_FOLDER_PATH}\n"
             f"URL: {URL}\n")


class ServiceTicket:
    def __init__(self, record_id, customer, comments):
        self.work_order_num = record_id
        self.customer = customer
        self.comments = comments
        self.file_list = []

        self._get_file_info()
        self._strip_name()

        self.save_path = os.path.join(SAVE_FOLDER_PATH, self.customer)

    def __repr__(self):
        return (
            f"WO NUM: {self.work_order_num} CUSTOMER: {self.customer} WO "
            f"TYPE: {self.comments}\n")

    def _get_file_info(self):
        response = requests.request('GET', f"{file_id_request}{self.work_order_num}", headers=headers)
        info = json.loads(response.text)
        for work_order_file in info:
            try:
                file = FileObject(self.work_order_num, work_order_file['id'], work_order_file['fileExtension'])
                self.file_list.append(file)
            except IndexError or KeyError as e:
                logger.error(f"FileObject creation failed: work_order: "
                             f"{work_order_file} ERROR: {e}")

    def _strip_name(self):
        self.customer = self.customer.upper()
        for i in range(10):
            for item in strip_list:
                self.customer = self.customer.removesuffix(item)

    def _create_folder(self):
        if not os.path.exists(self.save_path):
            os.mkdir(self.save_path)

    def download_files(self) -> int:
        total_downloads = 0
        self._create_folder()
        # Enumerate so that index can be appended to filename for wo's with multiple files
        for index, file in enumerate(self.file_list):
            new_filename = f"{self.work_order_num}({index}).{file.file_ext}"
            full_save_path = os.path.join(self.save_path, new_filename)
            download_url = f"{URL}/files/{file.file_id}/download"

            logger.debug(f"Downloading file: {file}\n")

            response = requests.request("GET", download_url, headers=headers,
                                        data=payload, allow_redirects=False)
            if response.status_code == 302:
                response_url = response.headers['Location']
                logger.info(f"File downloaded: {file}")
                with urllib.request.urlopen(response_url) as resp, open(full_save_path, 'wb') as new_file:
                    shutil.copyfileobj(resp, new_file)
                total_downloads += 1
            else:
                logger.error(f"FILE FAILED TO DOWNLOAD: {response.text}")
        return total_downloads



