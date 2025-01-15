import json
import os
import re
from datetime import datetime
from pathlib import Path

import openpyxl
import requests
from bs4 import BeautifulSoup, NavigableString
from dotenv import load_dotenv

from const import HEADERS, ACCOUNT_URL, ENV_USERNAME, HOME_URL, ENV_PASSWORD, LOGIN_URL, LOAD_BOOK_URL, \
    LOAD_MORE_URL, SEARCH_URL, SEARCH_DIR, SEARCH_XLS_FILENAME, EXISTING_COOKIE
from utils import get_url, post_url, get_cell_value, load_file_contents, get_search_filepath, get_partial_filepath


def login_with_existing_cookie():
    """
     Login the user in using an existing cookie (the cookie should already be logged in)
     NOTE: This doesn't actually log the user in, but it sets up the session with headers and checks that the cookie is valid.
    """
    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.update({'loginInitialized': 'true'})
    session.cookies.update({'PHPSESSID': EXISTING_COOKIE})
    # Check that the cookie is valid
    account_response = get_url(session, ACCOUNT_URL)
    soup = BeautifulSoup(account_response.text, 'html.parser')
    sign_out_button = soup.find('button', id='sign-out')
    if not sign_out_button:
        raise Exception('Login with existing cookie failed! The cookie has probably expired. Use login() to get a new cookie.')
    else:
        print('Using existing cookie ', EXISTING_COOKIE)
    return session


def login():
    """ Login to the ministrybooks.org server and get a cookie in the session """
    print('Logging in with user ', os.getenv(ENV_USERNAME))
    session = requests.Session()
    session.headers.update(HEADERS)

    # This will get a session cookie from the site
    get_url(session, HOME_URL)
    # Post the login credentials
    post_data = {
        'action': 'sign-in',
        'username': os.getenv(ENV_USERNAME),
        'password': os.getenv(ENV_PASSWORD),
        'stay-signed-in': 'on',
    }
    login_response = post_url(session, LOGIN_URL, post_data)
    soup = BeautifulSoup(login_response.text, 'html.parser')
    sign_out_button = soup.find('button', id='sign-out')
    if not sign_out_button:
        print('Login failed no sign-out in HTML! \n\n ', login_response.text, '\n\n\n')
        raise Exception('Login Failed! Could not find sign-out button on page after logging in.')
    else:
        session_cookie = None
        for cookie in session.cookies:
            if cookie.name == 'PHPSESSID':
                session_cookie = cookie.value
        print('Login successful using cookie ', session_cookie)
    return session


def search_contains(search_context, book_ref, snippet):
    """
    :return: true if the snippet has already been found in the book
    NOTE: page_num may be different because multiple snippets can be found on a page,
          and multiple page_nums point to the same web page
    """
    hits = search_context['data']['hits']
    for hit in hits:
        if hit['book_ref'] == book_ref and hit['snippet'] == snippet:
            return True
    return False


def get_book_snippet(search_context, book_html, book_ref, page_num):
    """
    Gets the paragraph containing the search term from the book page HTML
    NOTE: page numbers don't match web page size, so multiple page_num can point to the same web page, causing duplicates
    :param search_context: Context data for the search
    :param book_html: HTML containing the book text
    :param book_ref: String with the book reference
    :param page_num: Page number from link. NOTE: There may be multiple 'pages' on each HTML page
    :return: None : data will be added to search_context['data']
    """
    hits = search_context['data']['hits']
    soup = BeautifulSoup(book_html, 'html.parser')
    # Split the search term into tokens : searching for "(cyprian &! by birth) | jim" should result in a regex "cyprian|by birth|jim"
    tokens = []
    for token in re.split(r'&!|&|\||\^|\(|\)|\'-', search_context['data']['search_term']):
        if token.strip():
            tokens.append(token.strip().lower())
    regex_str = str.join('|', tokens)
    text_matches = soup.find_all(string=re.compile(regex_str, re.IGNORECASE))
    if not text_matches:
        print(f'Warning! Found no text matches using {regex_str}')
        if soup.find_all(string='not a robot'):
            raise ValueError(f'Rate limit hit!')
        else:
            raise ValueError(f'No text matches found in HTML \n\n{book_html} \n\n '
                             f'No text matches found!  book={book_ref}  page_num={page_num} using regex={regex_str}')
    for tag_match in text_matches:
        snippet = tag_match.get_text()
        if tag_match.name != 'p':
            parent_p = tag_match.find_parent('p')
            if parent_p:
                snippet = parent_p.get_text()
        if search_contains(search_context, book_ref, snippet):
            continue  # Skip this paragraph as it has already been recorded
        hits.append({
            'book_ref': book_ref,
            'page_num': page_num,
            'snippet': snippet,
        })
        print(f'Added pg. {page_num} using regex {regex_str}')


def load_book_results(search_context, list_item):
    """
    This loads the search results for a specific book
    :param search_context: Context data for the search
    :param list_item:  the LI tag (from beautiful soup) containing the link and the text
    """
    session = search_context['session']
    search_sess_id = search_context['search_sess_id']
    book_id = list_item['data-content']
    book_ref = ''
    for child_node in list_item.find():
        if not isinstance(child_node, NavigableString) and child_node.has_attr('class'):
            if 'hits' in child_node['class']:
                continue  # This skips printing the contents of <span class='hits'>3 hits</span>
        book_ref += child_node.text
    # Check if the book has already been processed (has existing hits with this book_ref)
    for hit in search_context['data']['hits']:
        if hit['book_ref'] == book_ref:
            print(f'Already finished book {book_ref}')
            return  # Exit this method (go to another book)
    # Load the book hits
    print(f'Loading book contents book_id={book_id} book_ref={book_ref}')
    post_data = {
        'content_key': book_id,
        'search_sess': search_sess_id,
    }
    response = post_url(session, LOAD_BOOK_URL, post_data)
    book_results_html = response.text
    soup = BeautifulSoup(book_results_html, 'html.parser')
    # Find all the top level p tags (each tag is a link to the page of a book)
    p_tags = soup.find_all('p', recursive=False)
    for p_tag in p_tags:
        page_num_tag = p_tag.find_next('strong', string=re.compile('^p. '))
        page_num = page_num_tag.text[3:].strip()  # Cut off the "p. "
        if page_num.endswith(':'):
            page_num = page_num[:-1]  # Strip off the trailing ":"
        a_tag = p_tag.find_next('a', class_='page-read-more')
        if not a_tag:
            print('Warning! Could not find a tag in p ', p_tag)
            continue
        href = a_tag['href']
        response = get_url(session, href)
        book_html = response.text
        get_book_snippet(search_context, book_html, book_ref, page_num)
    # If we get here we finished processing all the pages with hits in the book - write out a temp file
    first_name = search_context['data']['first_name']
    last_name = search_context['data']['last_name']
    with open(get_partial_filepath(first_name, last_name), 'w') as f:
        json.dump(search_context['data'], f)


def load_more_books(search_context, batch_num):
    """
    Clicks the load more button on the bottom of the page, looking for more books in the search
    Note: this is called recursively until there are no more pages
    """
    session = search_context['session']
    search_sess_id = search_context['search_sess_id']
    print('Load more search results batch=', batch_num)
    post_data = {
        'search_sess': search_sess_id,
        'batch_num': batch_num
    }
    response = post_url(session, LOAD_MORE_URL, post_data)
    load_more_data = response.json()
    chapter_html = load_more_data['chapter_html']
    soup = BeautifulSoup(chapter_html, 'html.parser')
    list_items = soup.find_all('li', class_='accordion-item')
    for list_item in list_items:
        load_book_results(search_context, list_item)
    # If there are more pages we will keep loading
    if load_more_data['more_batches']:
        load_more_books(search_context, batch_num + 1)


def search(session, search_term, first_name, last_name):
    print(f'\nSearching for {first_name} {last_name} using "{search_term}"')
    # Object to contain a lot of data that needs to get passed around (saves a long list of parameters)
    search_context = {'session': session,
                      'search_sess_id': None,
                      'data': {
                          'search_term': search_term,
                          'first_name': first_name,
                          'last_name': last_name,
                          'run_start': datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
                          'run_end': '',
                          'hits': [],  # Search results data
                      }}
    # Load partial results (so we don't have to re-request books if the search is interrupted)
    partial_file = get_partial_filepath(first_name, last_name)
    if Path(partial_file).is_file():
        search_context['data'] = json.loads(load_file_contents(partial_file))
    print('search context ', search_context)
    post_data = {'adv_search_scope': 'both',
                 'adv_search_text': search_term,
                 'adv_search_bk': '0',
                 'adv_search_pub': 'all',
                 'adv_search_year_start': '1922',
                 'adv_search_year_end': '1997',
                 'adv_search_titles_preload': [],
                 'adv_search_display': '250',
                 'adv_search_sort': 'hits',
                 'adv_search_submit': 'Search'}
    response = post_url(session, SEARCH_URL, post_data)
    search_html = response.text
    soup = BeautifulSoup(search_html, 'html.parser')

    # Get the search_sess_id
    form = soup.find('form', id='adv_search_callout')
    search_context['search_sess_id'] = form['data-search-sess']

    # Find the book links (each need to be expanded)
    ul = soup.find('ul', id='search-accordion')
    list_items = ul.find_all('li', class_='accordion-item')
    for list_item in list_items:
        load_book_results(search_context, list_item)

    # Find the "Load More" button
    load_more = soup.find('input', type='button', id='results_load_more')
    if load_more:
        load_more_books(search_context, 2)

    search_context['data']['run_end'] = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

    # Save the data collected for this search
    with open(get_search_filepath(first_name, last_name), 'w') as f:
        json.dump(search_context['data'], f)
    # Remove the partial file (temp)
    partial_filepath = Path(partial_file)
    if partial_filepath.is_file():
        partial_filepath.unlink()
        print('Deleted partial file ', partial_file)
    return


def load_search_terms():
    """
    Loads all the search terms from the Excel spreadsheet SEARCH_XLS_FILENAME, removes searches already completed
    :return: a list of objects with the data
    """
    search_terms = []
    workbook = openpyxl.load_workbook(SEARCH_XLS_FILENAME)
    worksheet = workbook.worksheets[0]
    found_filenames = os.listdir(SEARCH_DIR)
    existing_file_paths = []
    for existing_file in found_filenames:
        existing_file_paths.append(os.path.join(SEARCH_DIR, existing_file))
    print('found ', existing_file_paths)

    for row_index in range(2, worksheet.max_row + 1):
        first_name = get_cell_value(worksheet, row_index, 1)
        last_name = get_cell_value(worksheet, row_index, 2)
        search_term = get_cell_value(worksheet, row_index, 3)
        expected_filepath = get_search_filepath(first_name, last_name)
        if expected_filepath in existing_file_paths:
            print('Already searched for ', expected_filepath)
            continue
        if not search_term or not last_name:
            continue  # If there is no search term, this row is still a work in progress
        search_terms.append({
            'first_name': first_name,
            'last_name': last_name,
            'search_term': search_term,
        })
    return search_terms


def main():
    print('Start')
    session = login()
    # session = login_with_existing_cookie()
    search_terms = load_search_terms()
    for search_term in search_terms:
        search(session, search_term['search_term'], search_term['first_name'], search_term['last_name'])
    print('End')


load_dotenv()
main()
