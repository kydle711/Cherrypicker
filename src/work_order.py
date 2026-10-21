import json
import requests
import os
import shutil
import urllib.request
import logging
import traceback

from file_object import FileObject

from app_config import file_id_request, headers, URL, payload
from utils import load_config_json, strip_customer_name

logger = logging.getLogger(__name__)

logger.debug(f"Imported from config: \nfile_id_request: {file_id_request}\n"
             f"headers: {headers}\nURL: {URL}\n")


class WorkOrder:
    def __init__(self, record_id, customer, comments, sig_url):
        self.work_order_num = record_id
        self.customer = strip_customer_name(customer)
        self.comments = comments
        self.sig_url = sig_url
        self.sig_report_url = None
        self.file_list = []

        self._get_file_info()

        self.save_path = os.path.join(load_config_json("save_dir"), self.customer)
        self.signature_dir = os.path.join(self.save_path, "signatures")
        self._set_sig_report_url()

    def __repr__(self):
        return (
            f"WO NUM: {self.work_order_num} CUSTOMER: {self.customer} WO "
            f"TYPE: {self.comments}\n")

    def update_save_path(self, new_save_path):
        self.save_path = os.path.join(new_save_path, self.customer)

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

    def _set_sig_report_url(self):
        self.sig_report_url = self.sig_url.remove_suffix('sig.jpeg') + 'doc.pdf'

    def _create_signatures_folder(self):
        if not os.path.exists(self.signature_dir):
            try:
                os.mkdir(self.signature_dir)
            except Exception as e:
                logger.error(f"Failed to create signatures folder: {traceback.format_exc()}")
                self.signature_dir = self.save_path

    def _create_checklists_folder(self):
        if not os.path.exists(self.save_path):
            try:
                os.mkdir(self.save_path)
            except Exception as e:
                logger.error(f"Error making directory: {traceback.format_exc()}, Attempted save "
                             f"path: {self.save_path}")
                # Default to saving to root folder if an error occurs
                self.save_path = load_config_json("save_dir")

    def download_files(self) -> int:
        total_downloads = 0
        self._create_checklists_folder()
        # Enumerate so that index can be appended to filename for wo's with multiple files
        for index, file in enumerate(self.file_list):
            new_filename = f"{self.work_order_num}({index}).{file.file_ext}"
            full_save_path = os.path.join(self.save_path, new_filename)
            checklist_url = f"{URL}/files/{file.file_id}/download"

            logger.debug(f"Downloading file: {file}\n")

            response = requests.request("GET", checklist_url, headers=headers,
                                        data=payload, allow_redirects=False)
            if response.status_code == 302:
                # Redirect URL to cloudfront for file download
                response_url = response.headers['Location']
                logger.info(f"File downloaded: {file}")
                # Using urllib to download file, because requests headers won't work with redirect to cloudfront
                with urllib.request.urlopen(response_url) as resp, open(full_save_path, 'wb') as new_file:
                    shutil.copyfileobj(resp, new_file)
                total_downloads += 1
            else:
                logger.error(f"FILE FAILED TO DOWNLOAD: {response.text}")
        return total_downloads

    def download_signature(self):
        self._create_checklists_folder()
        self._create_signatures_folder()
        try:
            sig_image_filename = f"{self.work_order_num}-sig.jpg"
            image_save_path = os.path.join(self.signature_dir, sig_image_filename)

            with urllib.request.urlopen(self.sig_url) as resp, open(image_save_path, 'wb') as new_file:
                shutil.copyfileobj(resp, new_file)

            sig_report_filename = f"{self.work_order_num}-sig-report.pdf"
            report_save_path = os.path.join(self.signature_dir, sig_report_filename)

            with urllib.request.urlopen(self.sig_report_url) as resp, open(report_save_path, 'wb') as new_file:
                shutil.copyfileobj(resp, new_file)
        except Exception as e:
            logger.error(f"Error downloading signature: {traceback.format_exc()}")