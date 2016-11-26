# util.py

import csv

# Given a user or business id, hash and mod to get its node id
def getNId(id):
	return hash(id) % 100000

def getNIdDict(infile):
	NId_mapping = {}
	all_ids = set()
	user_ids = set()
	business_ids = set()
	with open(infile, 'r') as readFile:
		next(readFile)
		reader = csv.reader(readFile, delimiter='\t')
		for user_id, business_id in reader:
			all_ids.add(user_id)
			all_ids.add(business_id)
			user_ids.add(user_id)
			business_ids.add(business_id)

	return { getNId(data_id): data_id for data_id in all_ids }, { getNId(user_id): user_id for user_id in user_ids }, { getNId(business_id): business_id for business_id in business_ids }

# Returns a tuple of user and business node ids
def getUserBizNIds(G, businesses):
	userNIds = [NI.GetId() for NI in G.Nodes() if NI.GetId() not in businesses]
	bizNIds = [NI.GetId() for NI in G.Nodes() if NI.GetId() in businesses]
	return userNIds, bizNIds
