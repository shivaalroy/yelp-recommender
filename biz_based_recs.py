# biz-based-recs.py
# Provides business recommendations to users given their history of reviews

from const import Const
from json import dumps, loads
import math
import numpy as np
import operator
import snap
import sys
import types
from util import *

class BizBasedRecs(object):
	def __init__(self, G):
		self.G = G

	# Computes vectorized form business attributes
	# Returns: Map {business_nid: attribute vector}
	def getBusinessAttributes(self, AttrToIndx):
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
		edgeIds = set([NI.GetId() for NI in self.G.Nodes()])
		bizIds = set(attrDict.keys())
		return attrDict

	# Returns a mapping from business attribues to vector indices
	def getAttrIndxMapping(self):
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

	def getAvgAttr(self, businesses, attrDict):
		attrVecs = [np.array(attrDict[nid]) for nid in businesses]
		return np.average(attrVecs, axis=0)

	def score(self, dist):
		return math.exp(-dist)

	def getBusinessRecs(self, attrDict, k, scoreFunction):
		userNIds, businessNIds = getUserBizNIds(self.G, attrDict.keys())
		recs = {}
		for uid in userNIds:
			UI = self.G.GetNI(uid)
			businesses = [UI.GetNbrNId(n) for n in xrange(UI.GetDeg())] # get reviewed businesses
			avgAttr = self.getAvgAttr(businesses, attrDict)
			# print avgAttr
			bizScores = {}
			for bid in businessNIds:
				if bid not in businesses:
					BI = self.G.GetNI(bid)
					dist = np.linalg.norm(avgAttr - np.array(attrDict[bid]))
					# compute the scores using the scoring function
					if scoreFunction is not None:
						bizScores[bid] = scoreFunction(dist)
					else:
						bizScores[bid] = self.score(dist)
			topKBIds = sorted(bizScores, key=bizScores.get, reverse=True)[:k]
			# normalize scores for a given user
			for bid in topKBIds:
				recs[tuple(sorted((uid, bid)))] = bizScores[bid] / float(max(bizScores.values()))
		print recs
		return recs

	# Returns the top k recommendations for each user
	def getRecommendations(self, k, weightedMeans=False, weightedBusinesses=False, scoreFunction=None):
		# Loop through the businesses once to get attribute-vindex mapping
		AttrToIndx = self.getAttrIndxMapping()
		
		# for each business, calculate vectorized form of business attributes
		attrDict = self.getBusinessAttributes(AttrToIndx)
		
		# Get business recs for each user
		return self.getBusinessRecs(attrDict, k, scoreFunction)

def main(argv):
	G = snap.LoadEdgeList(snap.PUNGraph, Const.review_edge_list, 0, 1)
	Recommender = BizBasedRecs(G)
	Recommender.getRecommendations(1)

if __name__ == '__main__':
	main(sys.argv)
