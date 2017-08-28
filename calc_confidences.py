#!/usr/bin/env python

import string
import csv
import io
import sys
import math

def calculate_confidences(data, toxics):
	first = True
	fields = []
	for i in xrange(len(data)):

		product = data[i]

		# reading the metadata
		if first:
			fields = product[0].strip().split('\t')
			fields.append("CI_ Total")
			first = False

			data[i] = "\t".join(fields)
    		
		else:
			# split fields of current product
			prod = product[0].strip().split('\t')

			ingredients = get_ingredients(prod)
			subcategory = get_subcategory(prod)
    		
    		# calculate base confidence from numbers of toxins present
			total, bads, scaled, adjusted = calc_base(ingredients, toxics)

    		# add total ingredient number and number of bad stuff to end of row
			prod[8] = str(total)
			prod[9] = str(bads)
			prod[10] = str(scaled)
			prod[11] = str(adjusted)
			prod[12] = str(float(bads)/float(total))

			# increase confidence for interactions
			confidence = interactions(ingredients, subcategory, toxics, bads, adjusted)

			# increase confidence for products with high totals
			confidence = high_quantities(total, confidence)

			# ceiling at 100
			if confidence > 100:
				confidence = 100

			prod.append(str(confidence))

			data[i] = "\t".join(prod)

	return data

def get_ingredients(prod):
	# default ingredient list is field 6
	index = 6
	if len(prod) < 7:
		for c in xrange(len(prod)):
			# if there are multiple commas, choose this field
			if len(prod[c].split(',')) > 1:
				index = c

	ingredients = prod[index].split(',')
	for i in xrange(len(ingredients)):
		ingredients[i] = ingredients[i].strip().lower()
	return ingredients

def get_subcategory(prod):
	subcategory = prod[5].strip().lower()
	return subcategory

def calc_base(ingredients, toxics):
	# total number of ingredients
	total = len(ingredients)

	# check each ingredient for presence in toxics list
	bads = 0
	for chem in ingredients:
		if chem.strip().lower() in toxics:
			bads += 1

	# raise 2^x
	scaled = math.pow(2, bads)

	# cap at 100
	adj = scaled
	if scaled > 100:
		adj = 100

	return (total, bads, scaled, adj)

def interactions(ingredients, subcategory, toxics, bads, ci_base):
	heat_cats = ["hair", "exfoliants", "scrubs", "body-washes", "shave-products", "cleansers"]

	# different categories of toxins
	sulfates = get_toxics("sulfates.csv")
	diethanolamine = get_toxics("diethanolamine.csv")
	parabens = get_toxics("parabens.csv")
	pthalates = get_toxics("pthalates.csv")

	# check contents
	sulf = False
	dea = False
	par = False
	pthal = False
	for chem in ingredients:
		if chem in sulfates:
			sulf = True
		if chem in diethanolamine:
			dea = True
		if chem in parabens:
			par = True
		if chem in pthalates:
			pthal = True

	# sulfate-chemical interaction
	if sulf and dea:
		ci_base = increase_CI(ci_base, 2)
	elif sulf and bads > 1:
		ci_base =  increase_CI(ci_base, 1)

	# sulfate-heat interaction
	if subcategory.strip().lower() in heat_cats and sulf:
		ci_base = increase_CI(ci_base, 1)

	# DEA-paraben interaction
	if dea and par:
		ci_base = increase_CI(ci_base, 2)

	# pthalate interaction
	if pthal and bads > 1:
		ci_base = increase_CI(ci_base, 1)

	return ci_base

# increasing confidence interval for high ingredient counts
def high_quantities(total_num, ci_base):	
	lo = 20
	mid = 27
	hi = 57

	if total_num > lo and total_num < mid:
		ci_base = increase_CI(ci_base, 1)
	elif total_num > mid and total_num < hi:
		ci_base = increase_CI(ci_base, 1.5)
	elif total_num > hi:
		ci_base = increase_CI(ci_base, 2)

	return ci_base

def increase_CI(ci_base, scale):
	slope_constant = 1.329
	return ci_base * scale * slope_constant

def get_toxics(toxics_path):
	# reading in list of bad ingredients for checking
	toxics = []
	with open(toxics_path) as t_file:
		readCSV = csv.reader(t_file, delimiter=',')
		for row in readCSV:
			if len(row) > 0:
				toxics = row

	# strip white space and lower case
	for i in xrange(len(toxics)):
		toxics[i] = toxics[i].strip().lower()

	return toxics

def read_data(cosmetics_path):
	# get data from file, splitting on new lines
	with open(cosmetics_path, 'r') as f:
		data = [row for row in csv.reader(f.read().splitlines(), delimiter='\n')]

	return data

# write data to file
def write_new_data(data, path):
	with open(path, 'wb') as toWrite:
		for product in data:
			toWrite.write(product)
			toWrite.write('\n')

def main():
	toxics_path = "badstuff_2.csv"
	cosmetics_path = "cosmetics_new.tsv"
	output_path = "cosmetics_confidences.tsv"

	# get data from file
	toxics = get_toxics(toxics_path)
	data = read_data(cosmetics_path)

	# calculate confidences
	new_data = calculate_confidences(data, toxics)

	# write data to file
	write_new_data(new_data, output_path)

main()
