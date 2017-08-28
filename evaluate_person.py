#!/usr/bin/env python

import string
import csv
import io
import sys
import math
import calc_confidences as calc

def personal_confidence(person, product):
	toxics_path = "badstuff_2.csv"
	toxics = calc.get_toxics(toxics_path)

	ingredients = calc.get_ingredients(product)
	sulf, dea, par, pthal = calc.check_contents(ingredients)

	scalar = 1

	age = bucket_age(person["Age"])

	# teens
	if age == 1:
		if par or pthal or check_for(ingredients, "triclosan") or check_for(ingredients, "fragrance"):
			scalar = 2.25
		# triclosan, paraben, pthalate, fragrance

	# female
	if person["Sex"].strip().lower() == "female":
		# pthalate, paraben, toluene
		if par or pthal or check_for(ingredients, "toluene"):
			if age == 2:
				if "Pregnancy" in person and person["Pregnancy"] == 1:
					scalar = 2.5
				else:
					scalar = 1.75
			if age == 3:
				scalar = 1.5

	# male
	if person["Sex"].strip().lower() == "male":
		# oxybenzone, paraben, dmdh hydantoin, triclosan, fragrance
		if par or check_for(ingredients, "triclosan") or check_for(ingredients, "oxybenzone") or check_for(ingredients, "fragrance") or check_for(ingredients, "dmdh hydantoin"):
			if age == 2:
				if "Pregnancy" in person and person["Pregnancy"] == 1:
					scalar = 1.75
				else:
					scalar = 1.5
			if age == 3:
				scalar = 1.25

	prod_confidence = float(product[13].strip())

	new_confidence = prod_confidence * scalar
	return (prod_confidence, new_confidence)

def eval_person(person):
	products = person["Products"]
	confidence_sum = 0
	num_products = len(products)
	ingredients_total = []
	for prod in products:
		old_c, confidence = personal_confidence(person, prod)
		confidence_sum += confidence
		for chem in calc.get_ingredients(prod):
			ingredients_total.append(chem)

	toxics = calc.get_toxics("badstuff_2.csv")

	# calculate base confidence from numbers of toxins present
	total, bads, scaled, adjusted = calc.calc_base(ingredients_total, toxics)

	# increase confidence for interactions
	confidence = calc.interactions(ingredients_total, None, toxics, bads, adjusted)

	# normalize for number of products
	confidence = confidence/num_products

	# ceiling at 100
	if confidence > 100:
		confidence = 100

	confidence_avg = confidence_sum/num_products

	# ceiling at 100
	if confidence > 100:
		confidence = 100

	return (confidence, confidence_avg)


def check_for(ingredients, chemical):
	if chemical in ingredients:
		return True
	return False

def bucket_age(age):
	age = age.strip().lower()
	if age == "17 or younger".strip().lower():
		return 1
	elif age == "18 to 24".lower() or age == "25 to 34".lower() or age == "35 to 44".lower():
		return 2
	elif age == "45 to 54".lower() or age == "55 to 64".lower() or age == "65 to 74".lower() or age == "75 or older".lower():
		return 3
	else:
		return 0

if __name__ == '__main__':
	if len(sys.argv) > 2:
		print "Usage: evaluate_person.py <person> <products>"
	# a = sys.argv[1]