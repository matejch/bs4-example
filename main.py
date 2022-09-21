import sys

from detect import find_customer_subpage
from extract import extract_company_info
import csv

import requests

# TARGET_URL = "https://www.scale.com"
# TARGET_URL = 'https://amplitude.com'


# TARGET_URL ='https://www.pagerduty.com'
# TARGET_URL ='https://www.gusto.com'
TARGET_URL = 'https://www.rippling.com'
# TARGET_URL ='https://metabase.com'
# TARGET_URL ='https://posthog.com'
# TARGET_URL ='https://mailchimp.com'
# TARGET_URL ='https://convertkit.com'


def save_to_csv(company_list, url):
    fname = url.replace('https', '').replace('http', '').replace('://', '') + '.csv'
    with open(fname, 'w') as csvfile:
        fieldnames = ['company_logo', 'company_name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect='excel')
        writer.writeheader()
        for key_company in company_list:
            writer.writerow({'company_logo': key_company, 'company_name': company_list[key_company]})


def fix_relative_urls(company_list, domain):
    fixed = {}
    for company in company_list:
        if company.startswith('/'):
            fixed[domain + company] = company_list[company]
        else:
            fixed[company] = company_list[company]
    return fixed


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Usage: python scrape.py http://www.company.com")
        # sys.exit()
        INPUT_URL = TARGET_URL
    else:
        INPUT_URL = sys.argv[1]
    print("fetching data from {}".format(INPUT_URL))
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    result = requests.get(INPUT_URL, headers=headers)

    # try to find subpage with customers' information

    url, error = find_customer_subpage(result.content)

    if error:
        sys.exit("Could not find any data")

    result = requests.get(INPUT_URL + url, headers=headers)

    error, links, companies = extract_company_info(result.content, url)

    if error:
        # could not find data on this subpage. Trying one level deeper.
        if len(links) == 0:
            # we didn't get any links to follow, exiting
            sys.exit("No customer data found. No links found on {}".format(INPUT_URL))

        print("looking one level deeper")
        for link in links:
            print("looking one level deeper {}".format(INPUT_URL + link))
            result = requests.get(INPUT_URL + link, headers=headers)
            error, links, temp_companies = extract_company_info(result.content, link, 1)
            for company in temp_companies:
                companies[company] = temp_companies[company]
    companies = fix_relative_urls(companies, INPUT_URL)
    save_to_csv(company_list=companies, url=INPUT_URL)
    sys.exit("Successfully saved data from {}".format(INPUT_URL))
