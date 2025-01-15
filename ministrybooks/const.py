ENV_USERNAME = 'MINISTRYBOOKS_USERNAME'
ENV_PASSWORD = 'MINISTRYBOOKS_PASSWORD'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
HEADERS = {'User-Agent': USER_AGENT,
           'Content-type': 'application/x-www-form-urlencoded',
           'Accept': 'text/html',
           'host': 'www.ministrybooks.org',
           'origin': 'https://www.ministrybooks.org',
           'referer': 'https://www.ministrybooks.org/',
           }
EXISTING_COOKIE = 'bn6eu5vgbo92ng8hi19rtf5ni8'

HOME_URL = 'https://www.ministrybooks.org'
LOGIN_URL = 'https://www.ministrybooks.org/account/sign-in/post.php'
ACCOUNT_URL = 'https://www.ministrybooks.org/account/'
SEARCH_URL = 'https://www.ministrybooks.org/search/'
LOAD_MORE_URL = 'https://www.ministrybooks.org/search/utils/search_ajax_get_more_chapters.php'
LOAD_BOOK_URL = 'https://www.ministrybooks.org/search/utils/search_ajax_print_accordion_content.php'

SEARCH_DIR = 'searches'
SEARCH_XLS_FILENAME = 'search_terms.xlsx'

# Min / Max time to wait before making a network call
NETWORK_RATE_LIMIT_MIN_S = 2
NETWORK_RATE_LIMIT_MAX_S = 2
