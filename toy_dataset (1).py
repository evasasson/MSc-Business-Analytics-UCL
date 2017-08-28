#!/usr/bin/env python

import string
import csv
import io
import sys
import math
import random
import calc_confidences as calc
import evaluate_person as evalp
import demographic_analysis as demog

def main():

	dataset = []
	male = "Male"
	female = "Female"

	male_prods = get_products_cats("Male")
	female_prods = get_products_cats("Female")
	
	age = "17 or younger"
	dataset = create_age_group(age, False, 3, 9, dataset, male_prods, female_prods)

	age = "18 to 24"
	dataset = create_age_group(age, True, 7, 21, dataset, male_prods, female_prods)

	age = "25 to 34"
	dataset = create_age_group(age, True, 40, 110, dataset, male_prods, female_prods)

	age = "35 to 44"
	dataset = create_age_group(age, True, 50, 140, dataset, male_prods, female_prods)

	age = "45 to 54"
	dataset = create_age_group(age, True, 70, 180, dataset, male_prods, female_prods)

	age = "55 to 64"
	dataset = create_age_group(age, False, 50, 130, dataset, male_prods, female_prods)

	age = "65 to 74"
	dataset = create_age_group(age, False, 30, 90, dataset, male_prods, female_prods)

	age = "75 or older"
	dataset = create_age_group(age, False, 20, 50, dataset, male_prods, female_prods)

	demog.write_data(dataset, "generated_people.csv")


def create_age_group(age, preg, num_men, num_women, dataset, male_prods, female_prods):

	for i in xrange(num_men):
		new_person = {}
		new_person['Age'] = age
		new_person['Sex'] = "Male"

		if preg and i < int(num_men*0.4):
			p = 1
		else:
			p = 0
		new_person['Pregnancy'] = p

		if random.random() > 0.5:
			a = 1
		else:
			a = 0
		new_person["Animal_testing"] = a

		new_person["Products"] = assign_products("Male", male_prods)

		new_person["Product Names"] = []

		for prod in new_person["Products"]:
			new_person["Product Names"].append(prod[1])

		new_person["Number of Products"] = len(new_person["Products"])

		confidence, confidence_avg = evalp.eval_person(new_person)

		new_person["Bucket Confidence"] = confidence
		new_person["Confidence AVG"] = confidence_avg

		dataset.append(new_person)

	for i in xrange(num_women):
		new_person = {}
		new_person['Age'] = age
		new_person['Sex'] = "Female"

		if preg and i < int(num_women*0.44):
			p = 1
		else:
			p = 0
		new_person['Pregnancy'] = p

		if random.random() > 0.5:
			a = 1
		else:
			a = 0
		new_person["Animal_testing"] = a

		new_person["Products"] = assign_products("Female", female_prods)
		new_person["Product Names"] = []

		for prod in new_person["Products"]:
			new_person["Product Names"].append(prod[1])

		new_person["Number of Products"] = len(new_person["Products"])

		confidence, confidence_avg = evalp.eval_person(new_person)

		new_person["Bucket Confidence"] = confidence
		new_person["Confidence AVG"] = confidence_avg

		dataset.append(new_person)

	return dataset

def assign_products(sex, to_assign):

	if sex == "Male":
		num_products = int(random.random()*3) + 1

	elif sex == "Female":
		num_products = int(random.random()*5) + 2

	return random.sample(to_assign, num_products)

#return list of products depending on Sex
def get_products_cats(sex):
	cosmetics = calc.read_data("cosmetics_confidences.tsv")

	to_assign = []

	if sex == "Male":
		categories = calc.get_toxics("men_products.csv")

		for product in cosmetics[1:len(cosmetics)]:
			prod = product[0].split('\t')
			if calc.get_subcategory(prod) in categories:
				to_assign.append(prod)

	elif sex == "Female":
		for product in cosmetics[1:len(cosmetics)]:
			prod = product[0].split('\t')
			to_assign.append(prod)

	return to_assign

if __name__ == '__main__':
	main()