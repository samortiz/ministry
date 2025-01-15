import json
import os

from const import SEARCH_DIR
from utils import load_file_contents


def display_searches():
    filenames = os.listdir(SEARCH_DIR)
    for filename in filenames:
        search_data = json.loads(load_file_contents(os.path.join(SEARCH_DIR, filename)))
        first_name = search_data['first_name']
        last_name = search_data['last_name']
        hits = search_data['hits']
        print(f'\n\n{first_name} {last_name}\n')
        for hit in hits:
            print(f'- {hit["book_ref"]} pg. {hit["page_num"]}')
            print(f'{hit["snippet"]}\n')
        if 'partial' in filename:
            print(' ... incomplete data, there are more results that are not included ... \n')


display_searches()