# biz-recommender.py
# Provides business recommendations to users given their history of reviews

from json import dumps, loads
import snap
import sys
import types
from util import *

restaurantData = "./curated-data/restaurant_data.json"
reviewsFile = "./curated-data/reviews.txt"

# Computes vectorized form business attributes
# Returns: Map {business_nid: attribute vector}
def getBusinessAttributes():
	attrDict = {}
	# load business metadata
	with open(restaurantData, 'r') as f:
		for line in f:
			business = loads(line)
			attrVec = [] # TODO: sparse, and map attr name to index
			for attr in business['attributes']:
				val = business['attributes'][attr]
				if type(val) == types.BooleanType: # TODO: non-bool/deeper attr
					attrVec.append(int(val))
			attrDict[getNId(business['business_id'])] = attrVec
	return attrDict

def getBusinessRecs(G):
    pass

def main(argv):
	edgeListFile = createEdgeListFile()
	# load user / business edge list into undirected graph
	#G = snap.LoadEdgeList(snap.PUNGraph, edgeListFile, 0, 1)
	# for each business, calculate vectorized form of business attributes
	attributesDict = getBusinessAttributes()
	#getBusinessRecs(G)
	# for each user, get ids of businesses it reviewed
	# calculate the mean of the attribute vectors across businesses it reviewed
	# for all unreviewed businesses, calculate the distance to mean
	# return the k closest businesses

if __name__ == '__main__':
    main(sys.argv)
