import os
import json
import logging

from config import strip_list

logger = logging.getLogger(__name__)

def initialize_config_json():
    if not os.path.exists('config.json'):
        with open('config.json', 'w') as config_file:
            empty_config = {"last_scan": None, "save_dir": None, "customers": None}
            json.dump(empty_config, config_file, indent=4)

def load_config_json(param: str) -> str | None:
    try:
        with open('config.json', 'r') as f:
            data = json.load(f)
        return data.get(param)
    except (FileNotFoundError, json.JSONDecodeError) as json_error:
        logger.error(F"FAILED TO JSON PARAMETER: {param} ERROR: {json_error}")
        return None


def update_config_json(param: str, new_value: str | None):
    try:
        with open('config.json', 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as json_error:
        logger.error(f"FAILED TO LOAD DATA FOR REWRITE: {json_error}")
        data = {}

    data[param] = new_value

    with open('config.json', 'w') as f:
        json.dump(data, f, indent=4)


def flatten_data(raw_data):
    """Handles cases where the response contains multiple items with 'count' and
    'value' keys or where it just contains a single value with no keys."""
    if 'value' in raw_data.keys():
        return raw_data['value']
    else:
        return raw_data

def initialize_storage_folder(parent_dir=load_config_json(param="save_dir")) -> None:
    if not parent_dir:
        return
    if not os.path.exists(parent_dir):
        os.mkdir(parent_dir)


def strip_customer_name(customer_name: str) -> str:
    customer_name = customer_name.upper()
    for i in range(8):
        for item in strip_list:
            customer_name = customer_name.removesuffix(item)
    return customer_name