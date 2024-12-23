# Utility Methods
import os
import random
import re
import time
from pathlib import Path

from const import NETWORK_RATE_LIMIT_MIN_S, NETWORK_RATE_LIMIT_MAX_S, SEARCH_DIR


def network_delay():
    """
    This will pause for a little while to prevent overloading the server with requests
    """
    time.sleep(random.randint(NETWORK_RATE_LIMIT_MIN_S, NETWORK_RATE_LIMIT_MAX_S))


def load_file_contents(file_name):
    """
    Loads the contents of a file into a string (used to stub HTML calls)
    """
    with open(file_name, 'r') as file:
        file_text = file.read()
    return file_text


def post_url(session, url, post_data):
    """
    Handles posting to the server
    :param session: requests.Session
    :param url:  URL to post to
    :param post_data:  HTTP post data
    :return: response object
    """
    network_delay()
    response = session.post(url, data=post_data)
    return response


def get_url(session, url):
    """
    Gets a URL, returns the response object
    """
    network_delay()
    response = session.get(url)
    return response


def get_cell_value(worksheet, row_index, col_index):
    """
    Gets the value of a cell from a spreadsheet.  This will always return a string and never None
    """
    cell = worksheet.cell(row_index, col_index)
    if not cell or not cell.value:
        return ''
    value = str(cell.value)
    if not value:
        return ''
    return value


def get_full_path(filename, path=Path(SEARCH_DIR)):
    """ Returns a full path object to a file (including search dir)"""
    search_dir = path
    if not search_dir.exists():
        search_dir.mkdir(parents=True, exist_ok=True)
    return os.path.join(search_dir, filename)


def get_search_filepath(first_name, last_name):
    """
    Returns a path to the file for with the search data (completed search term)
    """
    first = first_name.lower().strip() if first_name else ''
    last = last_name.lower().strip() if last_name else ''
    alpha = re.compile('[^a-z]')
    return get_full_path(f's_{alpha.sub('', last)}_{alpha.sub('', first)}.json')


def get_partial_filepath(first_name, last_name):
    """
    Returns a path to a temp file which will contain partial search results.
    This will be updated after each book is processed to avoid re-requesting pages when a search is interrupted
    """
    first = first_name.lower().strip() if first_name else ''
    last = last_name.lower().strip() if last_name else ''
    alpha = re.compile('[^a-z]')
    return get_full_path(f's_{alpha.sub('', last)}_{alpha.sub('', first)}_partial.json')
