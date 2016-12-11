import csv

# Given a user or business id, hash and mod to get its node id
def getNId(yelp_id, user_id):
	margin = int(1e9)
	if user_id:
		return abs(hash(yelp_id)) % margin
	return (abs(hash(yelp_id)) % margin) + margin

def getBusinessNIdDict(infile):
	business_ids = set()
	with open(infile, 'r') as readFile:
		next(readFile)
		reader = csv.reader(readFile, delimiter='\t')
		for user_id, business_id in reader:
			business_ids.add(business_id)
	return { getNId(business_id, False): business_id for business_id in business_ids }

def getUserNIdDict(infile):
	user_ids = set()
	with open(infile, 'r') as readFile:
		next(readFile)
		reader = csv.reader(readFile, delimiter='\t')
		for user_id, business_id in reader:
			user_ids.add(user_id)
	return { getNId(user_id, True): user_id for user_id in user_ids }

# Returns a tuple of user and business node ids
def getUserBizNIds(G, businesses):
	userNIds = [NI.GetId() for NI in G.Nodes() if NI.GetId() not in businesses]
	bizNIds = [NI.GetId() for NI in G.Nodes() if NI.GetId() in businesses]
	return userNIds, bizNIds
