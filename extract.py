from typing import List, Hashable
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse
from constants import THRESHOLD, LOGO_WORDS


def is_target_word_in_alt_img(element):
    return does_attribute_contain_word(element, 'alt')


def is_target_word_in_src_img(element):
    return does_attribute_contain_word(element, 'src')


def does_attribute_contain_word(element, attribute):
    return element.name == 'img' and any([word in element.get(attribute, '') for word in LOGO_WORDS])


def remove_duplicates(links, tag, url=None):
    if len(links) == 0:
        return links
    results = set([link.get(tag, '') for link in links])  # remove duplicates
    if url:
        results.remove(url)  # remove origin
    return results


def extract_name_from_link(url):
    url = url.split('/')[-1] # we only need the last part of the url (customer name)
    return url.replace('-', ' ').capitalize()


def handle_next_image_url(url):
    if "url=" in urlparse(url).query:
        new_url = unquote(urlparse(url).query.replace('url=', ''))
        return new_url.split('&')[0]
    return url


def extract_company_info(html, origin_url, level=0) -> (bool, List, Hashable):
    result = {}
    links = []
    error = True

    soup = BeautifulSoup(html, 'html.parser')

    logos = soup.findAll(is_target_word_in_alt_img)
    logos2 = soup.findAll(is_target_word_in_src_img)

    if level == 0:
        links = soup.findAll(lambda element: element.name == 'a' and origin_url in element.get('href', ''))  # extract links that point to subpages (articles about a customer)  TODO: handle weird relative paths and absolute paths
        links = remove_duplicates(links, 'href', origin_url)
        # if we didn't find any logos, error is returned
        if len(logos) < THRESHOLD and len(logos2) < THRESHOLD:
            return True, links, {}

    # if deeper levels still don't yield any results we return and error and exit
    if len(logos) == 0 and len(logos2) == 0:
        return True, [], {}

    # at least one logo was found so we can parse the results
    companies = {}

    for img in logos:
        company_name = img.get('alt').replace('logo', '')
        company_logo = unquote(img.get('src'))
        companies[company_logo] = company_name.capitalize()

    for img in logos2:
        company_name = img.get('alt', '').replace('logo', '')
        if company_name == '' and level == 1:
            company_name = extract_name_from_link(origin_url)
        company_logo = handle_next_image_url(img.get('src'))
        companies[company_logo] = company_name.capitalize()

    return False, [], companies
