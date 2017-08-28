from selenium import webdriver
from bs4 import BeautifulSoup
import re
import requests
import json
import asyncio
import aiohttp

async def fetch(url, session):
    """Fetch response for run_product function
    """
    async with session.get(url) as response:
        try:
            return await response.read()
        except:
            return "Request error"

async def run_product(products, out):
    """Async function that gets list of products,
    gathers them as tasks, awaits server ressponses
    and appends them to out.
    """
    url = "http://www.sephora.com{0}"
    tasks = []
    async with aiohttp.ClientSession() as session:
        for p in products:
            task = asyncio.ensure_future(fetch(url.format(p), session))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        out.extend([x.decode('utf-8') for x in responses if x != 'Request error'])

final_output = []

#We iterate over 5 pages, gather response, parse it and extract individual products
products = []
for i in range(1,6):
    print(i)
    with requests.Session() as s:
        resp = s.get("http://www.sephora.com/search/search.jsp?keyword=ingredients&mode=all%26pag&pageSize=-1&currentPage={}".format(i))
        b = BeautifulSoup(resp.content)
        products.extend(json.loads(b.find('script', id='searchResult').text)['products']['products'])


    #extract product urls
    _products = [p['product_url'] for p in products]
    _out = []
    #async loop start
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run_product(_products, _out))
    loop.run_until_complete(future)
    #async loop finished

    for p in products:
        try:
            prod = {}
            prod['name'] = p['display_name']
            prod['brand'] = p['brand_name']
            try:
                prod['price'] = p['derived_sku']['list_price']
            except:
                prod['price'] = p['derived_sku']['list_price_min']
            prod['item_no'] = p['derived_sku']['sku_number']
            with requests.Session() as s:
                resp = s.get("http://www.sephora.com{0}".format(p['product_url']), timeout=3.0)
            b = BeautifulSoup(resp.content)
            product_json = json.loads(b.find('script', {'data-is-main-pdp-sku':'true'}).text)
            if 'ingredients' in product_json:
                prod['ingredients'] = product_json['ingredients']
            else:
                prod['ingredients'] = ''
            prod['category'] = re.search('"categoryPath=(.+)?"', resp.text).group(1).split(',')[-1]
            final_output.append(prod)
            print(len(final_output))
        except:
            print('E')

with open('output.json', 'w') as f:
    json.dump(final_output, f)


