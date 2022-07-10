from datetime import datetime
import logging
import json
import glob
from pathlib import Path
import os
import random
import string


# convert timestamp of 1636109100000 type
def convert_row_timestamp(timestamp):
    return datetime.utcfromtimestamp(
        timestamp / 1000).strftime(
        '%Y-%m-%d %H:%M:%S')


# return last row of pandas df as dict
def last_row_to_dict(data_frame):
    data = data_frame.copy()
    last_dict = data.tail(1)
    return last_dict.to_dict("records")[0]


# store last row to json file
def dict_to_json(row, file):
    time_current = datetime.utcnow()
    time = time_current.strftime(
        "%Y-%m-%d_%H:%M:%S")
    logging.info(f"storing data to file {file}_{time}.json")

    file_path = os.path.dirname(file)
    Path(file_path).mkdir(parents=True,
                          exist_ok=True)

    with open(f"{file}_{time}.json", "w") as _json:
        json.dump(row, _json, indent=4)


# locate last order file
def last_order(file):
    file_path = os.path.dirname(file)
    file_path = glob.iglob(f"{file_path}/*")
    try:
        last_file = max(file_path, key=os.path.getctime)
        logging.info(f"found previous order"
                     f" {Path(last_file).stem}")
        return last_file
    except ValueError:
        logging.info(f"no previous orders found")
        return False


# clean up order folder
def clean_up_order(file):
    _file = last_order(file)
    if not _file:
        logging.info("there is nothing to remove")
    else:
        logging.info(f"cleaning up {_file}")
        os.remove(_file)


# generate random string for client order id
def id_generator(size):
    return ''.join(random.SystemRandom().choice(
        string.ascii_uppercase + string.digits)
                   for _ in range(size))

