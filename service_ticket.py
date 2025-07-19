import json
import requests
import os
import shutil
import urllib.request

from file_object import FileObject

from config import file_id_request, headers, strip_list, SAVE_FOLDER_PATH, URL, payload


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
        return (f"WORK ORDER NUMBER: {self.work_order_num}\n"
                f"CUSTOMER NAME: {self.customer}\n"
                f"WORK ORDER TYPE: {self.comments}\n"
                f"FILE LIST: {self.file_list}")

    def _get_file_info(self):
        response = requests.request('GET', f"{file_id_request}{self.work_order_num}", headers=headers)
        info = json.loads(response.text)
        for work_order_file in info:
            try:
                file = FileObject(self.work_order_num, work_order_file['id'], work_order_file['fileExtension'])
                self.file_list.append(file)
            except IndexError or KeyError as e:
                print("File Object creation failed!")
                print(e)

    def _strip_name(self):
        self.customer = self.customer.upper()
        for i in range(5):
            for item in strip_list:
                self.customer = self.customer.removesuffix(item)

    def _create_folder(self):
        if not os.path.exists(self.save_path):
            os.mkdir(self.save_path)

    def download_files(self):
        self._create_folder()
        for index, file in enumerate(self.file_list):
            new_filename = f"{self.work_order_num}({index}).{file.file_ext}"
            full_save_path = os.path.join(self.save_path, new_filename)
            download_url = f"{URL}/files/{file.file_id}/download"
            response = requests.request("GET", download_url, headers=headers,
                                        data=payload, allow_redirects=False)
            if response.status_code == 302:
                response_url = response.headers['Location']
                with urllib.request.urlopen(response_url) as resp, open(full_save_path, 'wb') as new_file:
                    shutil.copyfileobj(resp, new_file)
            else:
                print(f"FAILED TO DOWNLOAD FILE {new_filename}")



