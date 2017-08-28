#!/usr/bin/env python

import string
import csv
import io
import sys
import calc_confidences as calc
import re

toxics_path = "badstuff_2.csv"
cosmetics_path = "boots_model.tsv"

# reading in list of bad ingredients for checking
toxics = calc.get_toxics(toxics_path)

# get counts for entire dataset and write to new file
with open('boots_with_counts.tsv', 'wb') as toWrite:
	with open(cosmetics_path, 'r') as f:
	    data = [row for row in csv.reader(f.read().splitlines(), delimiter='\n')]
	    first = True
	    fields = []
	    for product in data:

	    	if first:
	    		fields = product[0].strip().split('\t')
	    		fields.append("Number of Ingredients")
	    		fields.append("Number of Toxics")
	    		toWrite.write("\t".join(fields))
	    		toWrite.write('\n')
	    		first = False
	    		
	        else:
	    		prod = product[0].strip().split('\t')

	    		# some of the products had strange anomalies, this checks if the row has an abnormal amount of fields
	    		# usually the ingredient list is in the 6th field, but otherwise check for commas
	    		index = 4
	
	    		ingredients = re.split('; |, ',prod[index])
	    		
	    		# total number of ingredients, multiple splitting schemes
	    		total = len(ingredients)
	    		if total == 1 or (total < 3 and len(prod[index].split(' ')) > total):
	    			ingredients = prod[index].split('.')
	    			total = len(ingredients)
	    			if total == 1 or (total < 3 and len(prod[index].split(' ')) > total):
	    				ingredients = prod[index].split(' ')
	    				total = len(ingredients)

	    		# check each ingredient for presence in toxics list
	    		bads = 0
	    		for chem in ingredients:
	    			if chem.strip().lower().translate(None, string.punctuation) in toxics:
	    				bads += 1


	    		# add total ingredient number and number of bad stuff to end of row
	    		prod.append(str(total))
	    		prod.append(str(bads))

	    		# write to file
	    		toWrite.write("\t".join(prod))
	    		toWrite.write('\n')

