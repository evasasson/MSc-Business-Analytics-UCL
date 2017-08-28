
import json
from bs4 import BeautifulSoup
import sys
import urllib2
import csv
import httplib

# to set by the user
total_pages = 5 # Enter how many pages are displayed in pagination

httplib.HTTPConnection._http_vsn = 10				# the next 2 lines are for handling the incomplete response received by urllib2
httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'	
domain = "http://www.sephora.com"
item = {'product': '', 'brand': '', 'price': '', 'category1': '', 'category2': '', 'category3': '', 'item': 'ingredients' }

def encode_and_skip_lines(data_local):				# sanitizing the results
	return data_local.encode('utf-8').strip().replace('\n', ' ').replace('\r', '')

# Scraping each page accessed from the the pagination    
for page_nb in range(3, int(total_pages)+1):

	# read the page content and transform it into JSON 
	starting_page_url = 'http://www.sephora.com/rest/products/?keyword=ingredients&mode=allowed_domain%26pag&pageSize=-1&currentPage='+str(page_nb)+'&include_categories=true&include_refinements=true'
	req = urllib2.Request(starting_page_url, headers={'User-Agent':'Mozilla/5.0'})
	result = urllib2.urlopen(req)
	data = json.loads(result.read())
	with open("output3.csv",'a') as resultFile:
		wr = csv.writer(resultFile, delimiter=',')
		wr.writerow(['product','brand','price','category1', 'category2', 'category3', 'item','ingredients'])
		
		# looping over all items in current page, extracting a part of the wanted  data 
		for i in range(1,len(data["products"])):
			data_product = data["products"][i]
			derived_sku = data_product["derived_sku"]
			item['product'] = encode_and_skip_lines(data_product["display_name"])
			item['brand'] = encode_and_skip_lines(data_product["brand_name"])
			
			derived_sku = dict(derived_sku)
			
			try:
				item['price'] = encode_and_skip_lines(str(derived_sku["list_price"]))
			
			except KeyError:
				item['price'] = str(derived_sku["list_price_min"]).encode('utf-8') +"-" + str(derived_sku["list_price_max"]).encode('utf-8')
				item['price'] = encode_and_skip_lines(item['price'])

			product_url=  data_product["product_url"] # item
			
			# looping over all items in current page, extracting a part of the wanted  data
			req = urllib2.Request(domain+product_url, headers={'User-Agent':'Mozilla/5.0'}) 
			details_page = urllib2.urlopen(req)
			soup = BeautifulSoup(details_page)
			
			try:
				item['ingredients'] = encode_and_skip_lines(json.loads(soup.find('script', {'data-entity' : "Sephora.Sku"}).text)['ingredients'])
			except AttributeError:
				pass

			try:
				categories_list		= soup.find('ol' , {'class' : 'Breadcrumb'}).find_all('a' , {'class' : 'Breadcrumb-link'})
			except AttributeError:
				categories_list = []
				pass

			try:
				item['category1'] 	=  encode_and_skip_lines(categories_list[0].text)
			except IndexError:
				pass
			
			try:
				item['category2'] 	=  encode_and_skip_lines(categories_list[1].text)
			except IndexError:
				pass

			try:
				item['category3'] 	=  encode_and_skip_lines(categories_list[2].text)
			except IndexError:
				pass

			item['item'] = encode_and_skip_lines(str(derived_sku["sku_number"]))
			# for debuging 
			print 'parsing id' + str(i) + '....  product name ' + item['product']
			wr.writerow([item['product'] , item['brand'], item['price'], item['category1'], item['category2'], item['category3'], item['item'], item['ingredients']])