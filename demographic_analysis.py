#!/usr/bin/env python

import string
import csv
import io
import sys
import math
import random
import calc_confidences as calc
import evaluate_person as evalp

def main():
	demog_data = "demographic_segments.csv"
	
	people = load_data(demog_data)

	for i in xrange(len(people)):
		person = people[i]
		people[i] = assign_products(person)

	write_path = "demographic_products.csv"
	write_data(people, write_path)


def assign_products(person):
	confidence = 5
	category = person["Category"].strip().lower() #[2]
	price = int(person["Price"].strip().lower()) #[3]
	animal = int(person["Animal_testing"].strip().lower()) #[4]
	p_label = "Product "
	ct_label = "CI_Total "
	cp_label = "CI_Personal "
	num = 1
	while confidence > 4 and num < 7:
		product = preference_match(category, price, animal)
		if product == None:
			person[p_label + str(num)] = "None"
			break
		ci_total, ci_personal = evalp.personal_confidence(person, product)
		confidence = ci_personal

		person[p_label + str(num)] = product[1]
		person[ct_label + str(num)] = ci_total
		person[cp_label + str(num)] = ci_personal
		num += 1

	# print person
	# sys.exit()
	return person

def get_price_interval(rating):
	lo = 0
	hi = 1521
	if rating == 5:
		hi = 11
	elif rating == 4:
		lo = 11
		hi = 21.5
	elif rating == 3:
		lo = 21.5
		hi = 33
	elif rating == 2:
		lo = 33
		hi = 49
	elif rating == 1:
		lo = 49
	return (lo, hi)

def preference_match(category, price, animal):
	cosmetics_path = "cosmetics_confidences.tsv"
	matching_best = []
	matching_some = []
	matching_base = []

	data = calc.read_data(cosmetics_path)

	lo, hi = get_price_interval(price)

	first = True

	for i in xrange(len(data)):
		# print data[i][0].strip().split('\t')[7]
		# sys.exit()

		product = data[i][0].strip().split('\t')

		if first:
			first = False

		else:

			subc = calc.get_subcategory(product)
			cur_price = calc.get_price(product)

			anim = calc.get_animal_test(product)

			best = False
			some = False
			if subc == category:
				if cur_price != None and cur_price > lo and cur_price < hi:
					if animal == 0 and anim == 0:
						matching_best.append(product)
						best = True
					elif not best:
						matching_some.append(product)
						some = True
				elif not some:
					matching_base.append(product)

	if len(matching_best) > 0:
		to_pick = matching_best
	elif len(matching_some) > 0:
		to_pick = matching_some
	elif len(matching_base) > 0:
		to_pick = matching_base
	else:
		return None

	return random.choice(to_pick)

# loading demographic data as dictionary
def load_data(path):

	with open(path) as file:
		data = csv.DictReader(file)
		people = [x for x in data]

	return people

def write_data(people, path):
	lon = {}
	l = 0
	for p in people:
		if len(p) > l:
			l = len(p)
			lon = p
	with open(path, 'wb') as f:
		w = csv.DictWriter(f, lon.keys())
		w.writeheader()
		for person in people:
			w.writerow(person)

if __name__ == '__main__':
	if len(sys.argv) > 2:
		print "Usage: python demographic_analysis.py "
	# a = sys.argv[1]
	main()
	