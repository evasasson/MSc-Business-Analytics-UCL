# -*- coding: utf-8 -*-

import re
import json
from bs4 import BeautifulSoup
import sys
import urllib2
import csv
import httplib

echo "# MSc-Business-Analytics-UCL" >> README.md
git init
git add README.md
git commit -m "first commit"
git remote add origin https://github.com/evasasson/MSc-Business-Analytics-UCL.git
git push -u origin master


# the next 2 lines are for handling the incomplete response received by urllib2, 
#the last line is a workaround for max memory usage by multiprocessing
httplib.HTTPConnection._http_vsn = 10				
httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'	
sys.setrecursionlimit(50000)

# to set by the user
domain = "http://www.boots.com"
item = {'category': '', 'brand': '', 'Product': '', 'Price': '', 'Ingredients': '', 'us_uk' : '' }



def encode_and_skip_lines(data_local):				# sanitizing the results
	return data_local.encode('utf-8').strip().replace('\n', ' ').replace('\r', '')

def parsePage(no_of_page_to_parse, base_url_of_sub_category):
	print 'NEW PAGE'
	url = base_url_of_sub_category.replace('pageNo=1','pageNo='+str(no_of_page_to_parse))
	req = urllib2.Request(url, headers={'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'})
	response = urllib2.urlopen(req).read()
	return response

# for every item container, scrape interesting data 
def parseItem(item_link):
	item = {'category': '', 'brand': '', 'product': '', 'price': '', 'ingredients': '', 'us_uk' : ''}

	req = urllib2.Request(item_link, headers={'User-Agent':'Mozilla/5.0'})
	

	# Filling item and bypassing encoding issue!
	try:
		response = urllib2.urlopen(req).read().decode('utf8')
		soup_detailed_page = BeautifulSoup(response)
		item['us_uk'] =  'uk'
		item['brand'] =  encode_and_skip_lines(soup_detailed_page.find('input' , {'id' : 'productManufacturerName'}).attrs['value'])  #.attrs['value']
		# print soup_detailed_page.find_all('input' , {'id' : 'productManufacturerName'}).attrs['value']
		item['product'] =  encode_and_skip_lines(soup_detailed_page.find('h1' , {'itemprop' : 'name'}).text.encode('utf8'))
		item['price'] =  encode_and_skip_lines(soup_detailed_page.find('div' , {'class' : 'price'}).text)[2:]
	except:
		pass

	try:
		response = urllib2.urlopen(req).read().decode('ISO-8859-1').encode('utf8')
		soup_detailed_page = BeautifulSoup(response)
		item['us_uk'] =  'uk'
		item['brand'] =  encode_and_skip_lines(soup_detailed_page.find('input' , {'id' : 'productManufacturerName'}).attrs['value'])  #.attrs['value']
		# print soup_detailed_page.find_all('input' , {'id' : 'productManufacturerName'}).attrs['value']
		item['product'] =  soup_detailed_page.find('h1' , {'itemprop' : 'name'}).text
		item['price'] =  encode_and_skip_lines(soup_detailed_page.find('div' , {'class' : 'price'}).text)[2:]
		
	except:
		pass
	try:
		response = urllib2.urlopen(req).read()
		soup_detailed_page = BeautifulSoup(response)
		item['us_uk'] =  'uk'
		item['brand'] =  encode_and_skip_lines(soup_detailed_page.find('input' , {'id' : 'productManufacturerName'}).attrs['value'])  #.attrs['value']
		# print soup_detailed_page.find_all('input' , {'id' : 'productManufacturerName'}).attrs['value']
		item['product'] =  soup_detailed_page.find('h1' , {'itemprop' : 'name'}).text
		item['price'] =  encode_and_skip_lines(soup_detailed_page.find('div' , {'class' : 'price'}).text)[2:]
	except:
		pass
		
	
	try:
		if int(len(soup_detailed_page.find_all('div' , {'class' : 'product_long_description_subsection'}))) == 2:
			item['ingredients'] = soup_detailed_page.find_all('div' , {'class' : 'product_long_description_subsection'})[1].find('p').text
	except:
		item['ingredients'] = 'Not Found'
	return item

with open("output.csv",'a') as resultFile:
	wr = csv.writer(resultFile, delimiter=',')
	wr.writerow(['page', 'category' , 'Brand' , 'Product','price','ingredients', 'us_uk'])
	# defining variables
	category = 'cleansers'
	base_url1 = "http://www.boots.com/beauty/facial-skincare/cleanser-toner?contentBeginIndex=0&pageNo=1&productBeginIndex=48&beginIndex=48&orderBy=&facetId=&pageView=grid&resultType=products&orderByContent=&searchTerm=&facet=&facetLimit=&minPrice=&maxPrice=&pageSize=&prem=&article=&storeId=11352&catalogId=28501&langId=-1&objectId=_6_3074457345618262155_3074457345619312449&requesttype=html"


	req = urllib2.Request(base_url1, headers={'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.37 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'})
	response = urllib2.urlopen(req).read()
	soup_page = BeautifulSoup(response)
	total_pages = soup_page.find_all('div' , {'class' : 'pageControl'})[0].attrs['data-pages']
	total_pages = int(total_pages)
	for page_no in range(1, total_pages+1):    #   total_pages+1
		response = parsePage(page_no, base_url1)
		soup_page = BeautifulSoup(response)
		items_links = soup_page.find_all('div' , {'class' : 'product_name'})
		
		# insert in CSV file
		for item_link in items_links:
			# print page_no
			# print item_link.find('a' , {'aria-hidden' : 'true'}).attrs['href']
			item = parseItem(item_link.find('a' , {'aria-hidden' : 'true'}).attrs['href'])
			item['us_uk'] = 'us'
			item['category'] = category
			wr.writerow([page_no , item['category'], item['brand'] , encode_and_skip_lines(item['product'][1+len(item['brand']):]), item['price'], encode_and_skip_lines(item['ingredients']), item['us_uk']])