"""
Extracts features for restaurant businesses in the Yelp Challenge Dataset
"""

import csv
import os.path
import random
import sys
from collections import defaultdict
from json import dumps, loads
from re import sub

import util
from const import Const


def parseReview(json_infile, review_outfile, user_business_outfile, min_reviews=0, min_stars=0):
	reviews = []
	user_ids = defaultdict(int)
	with open(json_infile, 'r') as f:
		for line in f:
			review = loads(line)
			if int(review['stars']) >= min_stars:
				user_ids[review['user_id']] += 1
				reviews.append(review)
	print 'Total Reviews with at least', min_stars ,'stars:', len(reviews)

	if min_reviews:
		user_ids = set(key for key, val in  user_ids.iteritems() if val >= min_reviews)
		reviews = [review for review in reviews if review['user_id'] in user_ids]
		print 'Filtered Reviews by users with at least', min_reviews ,'reviews:', len(reviews)

	business_ids = set()
	edges = []
	for review in reviews:
		business_ids.add(str(review['business_id']))
		edges.append(str(review['user_id'])+'\t'+str(review['business_id']))

	with open(review_outfile,'w') as reviews_file:
		for review in reviews:
			reviews_file.write(dumps(review))
			reviews_file.write('\n')
	with open(user_business_outfile,'w') as edges_file:
		edges_file.write('#user_id\tbusiness_id\n')
		for edge in edges:
			edges_file.write(edge)
			edges_file.write('\n')
	return set(user_ids), business_ids


def parseUser(json_infile, user_outfile, friend_outfile, user_ids):
	users = []
	edges = []
	with open(json_infile, 'r') as f:
		for line in f:
			user = loads(line)
			if user['user_id'] in user_ids:
				users.append(user)
				for friend in user['friends']:
					if user['user_id'] < friend:
						edges.append(user['user_id']+'\t'+friend)
	print 'Total Users:', len(users)

	with open(user_outfile,'w') as users_file:
		for user in users:
			users_file.write(dumps(user))
			users_file.write('\n')
	with open(friend_outfile,'w') as edges_file:
		edges_file.write('#user_id\tfriend\n')
		for edge in edges:
			edges_file.write(edge)
			edges_file.write('\n')


def parseBusiness(json_infile, business_outfile, business_ids):
	businesses = []
	with open(json_infile, 'r') as f:
		for line in f:
			business = loads(line)
			if 'Restaurants' in business['categories'] and business['city'] == 'Las Vegas' and business['business_id'] in business_ids:
				businesses.append(business)
	print 'Total Restaurants:', len(businesses)

	with open(business_outfile,'w') as businesses_file:
		for business in businesses:
			businesses_file.write(dumps(business))
			businesses_file.write('\n')


def filterLocaleReviews(business_infile, review_infile, locale_outfile):
	locale_ids = set()
	with open(business_infile, 'r') as f:
		for line in f:
			business = loads(line)
			if ('Restaurants' in business['categories']) and (business['city'] == 'Las Vegas'):
				locale_ids.add(business['business_id'])

	lineCount = 0
	with open(review_infile, 'r') as readFile, open(locale_outfile, 'w') as writeFile:
		for line in readFile:
			review = loads(line)
			if review['business_id'] in locale_ids:
				writeFile.write(dumps(review))
				writeFile.write('\n')
				lineCount += 1
	print 'Las Vegas reviews:', lineCount


def createEdgeList(user_biz_infile, edge_outfile):
	user_ids = set()
	business_ids = set()
	with open(user_biz_infile, 'r') as readFile, open(edge_outfile, 'w') as writeFile:
		next(readFile) # skip heading
		writeFile.write('#user_id\tbusiness_id\n')
		reader = csv.reader(readFile, delimiter='\t')
		for user_id, business_id in reader:
			user_ids.add(user_id)
			business_ids.add(business_id)
			writeFile.write(str(util.getNId(user_id, True))+'\t'+str(util.getNId(business_id, False))+'\n')

	hash_ids = {}
	for user_id in user_ids:
		if util.getNId(user_id, True) in hash_ids:
			print '--ERROR-- user', hash_ids[util.getNId(user_id, True)], user_id
		hash_ids[util.getNId(user_id, True)] = user_id

	for business_id in business_ids:
		if util.getNId(business_id, False) in hash_ids:
			print '--ERROR-- business', hash_ids[util.getNId(business_id, False)], business_id
		hash_ids[util.getNId(business_id, False)] = business_id


def main():
	if not os.path.isfile(Const.las_vegas_review):
		print Const.las_vegas_review, 'not found, parsing', Const.yelp_review
		filterLocaleReviews(Const.yelp_business, Const.yelp_review, Const.las_vegas_review)
		print 'Done parsing, created', Const.las_vegas_review

	print 'Parsing', Const.las_vegas_review
	user_ids, business_ids = parseReview(Const.las_vegas_review, Const.curated_review, Const.review_mapping, min_reviews=150, min_stars=4)
	print 'Done parsing', Const.las_vegas_review

	print 'Parsing', Const.yelp_user
	parseUser(Const.yelp_user, Const.curated_user, Const.friend_mapping, user_ids)
	print 'Done parsing', Const.yelp_user

	print 'Parsing', Const.yelp_business
	parseBusiness(Const.yelp_business, Const.curated_business, business_ids)
	print 'Done parsing', Const.yelp_business

	print 'Creating edge lists'
	createEdgeList(Const.review_mapping, Const.review_edge_list)
	createEdgeList(Const.friend_mapping, Const.friend_edge_list)
	print 'Done creating edge lists'

if __name__ == '__main__': main()
