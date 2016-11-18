# biz-recommender.py
# Provides business recommendations to users given their history of reviews

from json import dumps, loads
import numpy as np
import snap
import sys
import types
from util import *

restaurantData = 'curated-data/restaurant_data.json'
reviewsFile = 'curated-data/reviews.txt'
edgeListFile = 'curated-data/edge_list.json'

# Computes vectorized form business attributes
# Returns: Map {business_nid: attribute vector}
def getBusinessAttributes(G):
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
			nid = getNId(business['business_id'])
			attrDict[getNId(business['business_id'])] = attrVec
	edgeIds = set([NI.GetId() for NI in G.Nodes()])
	bizIds = set(attrDict.keys())
	print attrDict
	return attrDict

def getAvgAttr(businesses, attrDict):
	#print businesses
	attrVecs = [np.array(attrDict[nid]) for nid in businesses]
	print [len(attrDict[nid]) for nid in businesses]
	print [attrDict[nid] for nid in businesses]
	#print attrVecs
	return np.average(attrVecs, axis=0)

def getBusinessRecs(G, attrDict):
	print "num nodes", G.GetNodes()
	nusers = 0
	for NI in G.Nodes():
		if NI.GetId() not in attrDict: # check this is a user node
			nusers += 1
			#print NI.GetDeg()
			businesses = [NI.GetNbrNId(n) for n in xrange(NI.GetDeg())] # get neighbor ids (reviewed businesses)
			#print "number of businesses reviewed:", len(businesses)
			avgAttr = getAvgAttr(businesses, attrDict)
			print "avgAttr: %s" % avgAttr
	print "num users", nusers

def main(argv):
	createEdgeListFile()
	# load user / business edge list into undirected graph
	G = snap.LoadEdgeList(snap.PUNGraph, edgeListFile, 0, 1)
	# for each business, calculate vectorized form of business attributes
	attrDict = getBusinessAttributes(G)
	# print G.GetNodes()
	# print [NI.GetId() for NI in G.Nodes()]
	# print attrDict.keys()
	# print len(attrDict.keys())
	# print set(attrDict.keys()) - (set(attrDict.keys()) - set([NI.GetId() for NI in G.Nodes()]))
	getBusinessRecs(G, attrDict)
	# for each user, get ids of businesses it reviewed
	# calculate the mean of the attribute vectors across businesses it reviewed
	# for all unreviewed businesses, calculate the distance to mean
	# return the k closest businesses

if __name__ == '__main__':
	main(sys.argv)
