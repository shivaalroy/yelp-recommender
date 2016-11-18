# biz-based-recs.py
# Provides business recommendations to users given their history of reviews

from const import Const
from json import dumps, loads
import numpy as np
import snap
import sys
import types
from util import *

def getAttrIndxMapping():
	AttrToIndx = {}
	i = 0
	with open(Const.curated_business, 'r') as f:
		for line in f:
			business = loads(line)
			for attr in business['attributes']:
				val = business['attributes'][attr]
				if type(val) == types.BooleanType: # TODO: non-bool/deeper attr
					if attr not in AttrToIndx:
						AttrToIndx[attr] = i
						i += 1
				elif attr == "Good For" or attr == "Ambience":
					for item in val:
						if item not in AttrToIndx:
							AttrToIndx[item] = i
							i += 1
	return AttrToIndx

# Computes vectorized form business attributes
# Returns: Map {business_nid: attribute vector}
def getBusinessAttributes(G, AttrToIndx):
	attrDict = {}
	# load business metadata
	with open(Const.curated_business, 'r') as f:
		for line in f:
			business = loads(line)
			attrVec = [0] * len(AttrToIndx)
			for attr in business['attributes']:
				val = business['attributes'][attr]
				if type(val) == types.BooleanType: # TODO: non-bool/deeper attr
					attrVec[AttrToIndx[attr]] = int(val)
				elif attr == "Good For" or attr == "Ambience":
					for item in val:
						attrVec[AttrToIndx[item]] = int(val[item])
			nid = getNId(business['business_id'])
			attrDict[getNId(business['business_id'])] = attrVec
	edgeIds = set([NI.GetId() for NI in G.Nodes()])
	bizIds = set(attrDict.keys())
	return attrDict

def getAvgAttr(businesses, attrDict):
	attrVecs = [np.array(attrDict[nid]) for nid in businesses]
	return np.average(attrVecs, axis=0)

def getBusinessRecs(G, attrDict):
	userNIds, businessNIds = getUserBizNIds(G, attrDict.keys())
	recs = {}
	for uid in userNIds:
		UI = G.GetNI(uid)
		businesses = [UI.GetNbrNId(n) for n in xrange(UI.GetDeg())] # get reviewed businesses
		if len(businesses) > 5:	# TODO: filter in parsing step
			avgAttr = getAvgAttr(businesses, attrDict)
			dist = {}
			for bid in businessNIds:
				if bid not in businesses:
					BI = G.GetNI(bid)
					dist[bid] = np.linalg.norm(avgAttr - np.array(attrDict[bid]))
			recs[uid] = min(dist, key=dist.get)
	print recs
	# print "num >5 reviews:" , len([NI.GetDeg() for NI in G.Nodes() if NI.GetDeg() > 10])
	# for NI in G.Nodes():
	# 	i += 1
	# 	if NI.GetId() not in attrDict: # check it's a user node
	# 		businesses = [NI.GetNbrNId(n) for n in xrange(NI.GetDeg())] # get reviewed businesses
	# 		if len(businesses) > 5:	
	# 			nrecs += 1
	# 			print len(businesses)
	# 		avgAttr = getAvgAttr(businesses, attrDict)
	# 		dist = {}
	# 		for NI2 in G.Nodes():
	# 			if NI2.GetId() in attrDict and NI2.GetId() not in businesses:
	# 				dist[NI2.GetId()] = np.linalg.norm(avgAttr - np.array(attrDict[NI2.GetId()]))
	# 		print min(dist.values())
	# print "number of recs", nrecs

def main(argv):
	# load user / business edge list into undirected graph
	G = snap.LoadEdgeList(snap.PUNGraph, Const.review_edge_list, 0, 1)
	
	# Loop through the businesses onces to get attribute-vindex mapping
	AttrToIndx = getAttrIndxMapping()
	
	# for each business, calculate vectorized form of business attributes
	attrDict = getBusinessAttributes(G, AttrToIndx)
	
	# Get business recs for each user
	getBusinessRecs(G, attrDict)
	
	# for all unreviewed businesses, calculate the distance to mean
	# return the k closest businesses

if __name__ == '__main__':
	main(sys.argv)
