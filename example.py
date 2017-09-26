import sys
from GoogleScraper import scrape_with_config, GoogleSearchError
from GoogleScraper.database import ScraperSearch, SERP, Link

from os.path import abspath, dirname, join

import pickle
import requests
import csv

file =  '/Users/ebagdasaryan/Documents/development/instacart_2017_05_01/products.csv'
save = '/Users/ebagdasaryan/Documents/development/instacart_2017_05_01/save.pkl'
anti_counter = 0
# product_list = list()
# with open(file) as f:
#     print('open file %s' % file)
#     field_names = (f.readline().split('\n')[0]).split(',')
#     print(field_names)
#
#     for iterator, entry in enumerate(csv.reader(f)):
#         entry_dict = dict()
#         if iterator % 10000 == 0:
#             print(iterator)
#         for x, y in zip(field_names, entry):
#             entry_dict[x] = y
#         # input_list.append(entry_dict)
#         product_list.append(entry_dict)

def save_file(obj, file):
    with open(file, 'wb') as f:
        pickle.dump(obj=obj, file=f, protocol=pickle.HIGHEST_PROTOCOL)


with open('/Users/ebagdasaryan/Documents/development/instacart_2017_05_01/save.pkl', 'rb') as f:
    product_list = pickle.load(file=f)


# very basic usage
def basic_usage(products_parsed):
    local_anti = 0
    # See in the config.cfg file for possible values
    keywords = [y for x, y in products_parsed]
    config = {

        'use_own_ip': 'True',
        'search_engines': ['bing',],
        'num_pages_for_keyword': 1,
        'num_results_per_page': 20,
        'num_workers': step,

        'keywords': keywords,
        'SELENIUM': {
            'sel_browser': 'chrome',
        },

        'do_caching': 'True'

    }

    try:
        sqlalchemy_session = scrape_with_config(config)
    except GoogleSearchError as e:
        print(e)

    # let's inspect what we got
    serps = sqlalchemy_session.serps
    loop = dict()
    for it, serp in enumerate(serps):
        loop[serp.query] = list()
        for link in serp.links:
             loop[serp.query].append({'link': link.link, 'title': link.title})

    for it in products_parsed:
        links = loop.get(it[1], None)
        if not links:
            local_anti += 1
            continue

        for link in links:

            if 'product' in link['link'] and 'instacart' in link['link']:
                req = requests.get(url=link['link'])
                if req.status_code!=404:
                    product_list[it[0]]['link'] = link['link']
                    product_list[it[0]]['title'] = link['title']
                    product_list[it[0]]['content'] = req.content
                    break
                else:
                    product_list[it[0]]['link'] = link['link']
                    product_list[it[0]]['title'] = link['title']
                    product_list[it[0]]['content'] = None

        if not product_list[it[0]].get('link', False):
            local_anti += 1


    return local_anti

import time

total_count = 0
step = 5
for it in range(0, len(product_list), step):

    t1 = time.time()
    # time.sleep(1)


    products_parsed = list()
    for iterator in range(it, it+step):
        products_parsed.append((iterator, 'site:instacart.com {0}'.format(product_list[iterator]['product_name'])))

    anti_counter += basic_usage(products_parsed)

    # if not link:
    #     anti_counter +=1
    #     print(anti_counter)

    save_file(product_list, save)
    print('total: {0}. anti: {1}. time: {2}'.format(it, anti_counter, time.time()-t1))

