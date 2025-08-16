import os
import json
import logging
import traceback

from config import strip_list, CONFIG_FILE

logger = logging.getLogger(__name__)


def initialize_config_json(config_file=CONFIG_FILE) -> None:
    if not os.path.exists(config_file):
        with open(config_file, 'w') as config_file:
            empty_config = {"last_scan": None, "save_dir": None, "customers": None}
            json.dump(empty_config, config_file, indent=4)


def load_config_json(param: str, config_file=CONFIG_FILE) -> str | dict | None:
    try:
        with open(config_file, 'r') as f:
            data = json.load(f)
        return data.get(param)
    except Exception as e:
        logger.error(f"Encountered error on load_config_json: {traceback.format_exc()}")
        return None


def update_config_json(param: str, new_value: str | dict | None, config_file=CONFIG_FILE) -> None:
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
    except Exception as e:
        logger.error(f"Encountered error on update_config_json: {traceback.format_exc()}")
        config_data = {}

    config_data[param] = new_value

    with open(config_file, 'w') as f:
        json.dump(config_data, f, indent=4)


def flatten_data(raw_data: list | dict) -> list | dict:
    """Handles cases where the response contains multiple items with 'count' and
    'value' keys or where it just contains a single value with no keys."""
    if 'value' in raw_data.keys():
        return raw_data['value']
    else:
        return raw_data

def initialize_storage_folder(parent_dir=None) -> None:
    if parent_dir is None:
        parent_dir = load_config_json(param="save_dir")
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