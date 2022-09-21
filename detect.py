from bs4 import BeautifulSoup
from constants import CUSTOMER_SUBPAGE_WORDS


def find_customer_subpage(html):
    soup = BeautifulSoup(html, 'html.parser')
    error = True
    result = ""

    links = soup.findAll('a')
    for link in links:
        for trigger in CUSTOMER_SUBPAGE_WORDS:
            if trigger in link.attrs.get('href', ''):
                return link.attrs['href'], False

    return result, error
