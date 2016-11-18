"""
Extracts features for restaurant businesses in the Yelp Challenge Dataset
"""

import csv
import os.path
import random
import sys
import util
from const import Const
from json import loads
from json import dumps
from re import sub

def parseBusiness(json_infile, business_outfile, num_businesses=100):
	data = []
	locale_ids = set()
	with open(json_infile, 'r') as f:
		for line in f:
			business = loads(line)
			if ('Restaurants' in business['categories']) and (business['city'] == 'Las Vegas'):
				data.append(business)
				locale_ids.add(business['business_id'])
	print 'Total Restaurants:', len(data)

	sampled_data = random.sample(data, num_businesses)
	print 'Shrunk it to:', len(sampled_data)

	business_ids = set()
	for business in sampled_data:
		business_ids.add(business['business_id'])

	with open(business_outfile,'w') as data_file:
		for business in sampled_data:
			data_file.write(dumps(business, data_file))
			data_file.write('\n')
	return business_ids, locale_ids

def filterLocaleReviews(json_infile, locale_outfile, locale_ids):
	lineCount = 0
	with open(json_infile, 'r') as readFile, open(locale_outfile, 'w') as writeFile:
		for line in readFile:
			review = loads(line)
			if review['business_id'] in locale_ids:
				writeFile.write(dumps(review))
				writeFile.write('\n')
				lineCount += 1
	print 'Las Vegas reviews:', lineCount


def parseReview(json_infile, review_outfile, user_business_outfile, business_ids):
	data = []
	edges = []
	user_ids = set()
	with open(json_infile, 'r') as f:
		for line in f:
			review = loads(line)
			if review['business_id'] in business_ids:
				data.append(review)
				edges.append(str(review['user_id'])+'\t'+str(review['business_id']))
				user_ids.add(review['user_id'])
	print 'Total Reviews:', len(data)

	with open(review_outfile,'w') as data_file:
		for review in data:
			data_file.write(dumps(review, data_file))
			data_file.write('\n')
	with open(user_business_outfile,'w') as edges_file:
		edges_file.write('#user_id\tbusiness_id\n')
		for edge in edges:
			edges_file.write(edge)
			edges_file.write('\n')
	return user_ids

def parseUser(json_infile, user_outfile, friend_outfile, user_ids):
	data = []
	edges = []
	with open(json_infile, 'r') as f:
		for line in f:
			user = loads(line)
			if user['user_id'] in user_ids:
				data.append(user)
				for friend in user['friends']:
					if user['user_id'] < friend:
						edges.append(user['user_id']+'\t'+friend)
	print 'Total Users:', len(data)

	with open(user_outfile,'w') as data_file:
		for user in data:
			data_file.write(dumps(user, data_file))
			data_file.write('\n')
	with open(friend_outfile,'w') as edges_file:
		edges_file.write('#user_id\tfriend\n')
		for edge in edges:
			edges_file.write(edge)
			edges_file.write('\n')

def createEdgeList(user_biz_infile, edge_outfile):
	all_ids = set()
	with open(user_biz_infile, 'r') as readFile, open(edge_outfile, 'w') as writeFile:
		next(readFile) # skip heading
		reader = csv.reader(readFile, delimiter='\t')
		for user_id, business_id in reader:
			writeFile.write(str(util.getNId(user_id))+'\t'+str(util.getNId(business_id))+'\n')

	hash_ids = set()
	for str_id in all_ids:
		if util.GetNId(str_id) in hash_ids: exit('ERROR')
		hash_ids.add(util.getNId(user_id))
		hash_ids.add(util.getNId(business_id))

def main(argv):
	print 'Parsing', Const.yelp_business
	business_ids, locale_ids = parseBusiness(Const.yelp_business, Const.curated_business, 100)
	print 'Done parsing', Const.yelp_business

	if not os.path.isfile(Const.las_vegas_review):
		print Const.las_vegas_review, 'not found, parsing', Const.yelp_review
		filterLocaleReviews(Const.yelp_review, Const.las_vegas_review, locale_ids)
		print 'Done parsing', Const.yelp_review, 'created'

	print 'Parsing', Const.las_vegas_review
	user_ids = parseReview(Const.las_vegas_review, Const.curated_review, Const.review_mapping, business_ids)
	print 'Done parsing', Const.las_vegas_review

	print 'Parsing', Const.yelp_user
	parseUser(Const.yelp_user, Const.yelp_user, Const.friend_mapping, user_ids)
	print 'Done parsing', Const.yelp_user

	print 'Creating edge lists'
	createEdgeList(Const.review_mapping, Const.review_edge_list)
	createEdgeList(Const.friend_mapping, Const.friend_edge_list)
	print 'Done creating edge lists'

if __name__ == '__main__':
	main(sys.argv)
