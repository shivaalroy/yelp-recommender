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
import util


class BizBasedRecs(object):
	def __init__(self, G):
		self.G = G
		# Loop through the businesses once to get attribute-vindex mapping
		self.__getAttrIndxMapping()
		# for each business, calculate vectorized form of business attributes
		self.__getBusinessAttributes()

		# x = sorted([(index,attr) for attr,index in self.attrToIndx.iteritems()])
		# for index,attr in x:
		# 	print index,attr

	# Returns a mapping from business attribues to vector indices
	def __getAttrIndxMapping(self):
		self.attrToIndx = {}
		i = 0
		with open(Const.curated_business, 'r') as f:
			for line in f:
				business = loads(line)
				if 'stars' not in self.attrToIndx:
					self.attrToIndx['stars'] = i
					i += 1
				for attr, val in business['attributes'].iteritems():
					if type(val) == types.BooleanType: # TODO: non-bool/deeper attr
						if attr not in self.attrToIndx:
							self.attrToIndx[attr] = i
							i += 1
					elif attr == 'Good For' or attr == 'Ambience':
						prefix = 'Good For ' if attr == 'Good For' else 'Ambience '
						for item in val:
							key = prefix + item
							if key not in self.attrToIndx:
								self.attrToIndx[key] = i
								i += 1
					elif attr == 'Price Range':
						if attr not in self.attrToIndx:
							self.attrToIndx[attr] = i
							i += 1
				for category in business['categories']:
					if category != 'Restaurants' and category not in self.attrToIndx:
						self.attrToIndx[category] = i
						i += 1

	# Computes vectorized form business attributes
	# Returns: Map {business_nid: attribute vector}
	def __getBusinessAttributes(self):
		self.attrDict = {}

		# count = True

		# load business metadata
		with open(Const.curated_business, 'r') as f:
			for line in f:
				business = loads(line)
				attrVec = [0] * len(self.attrToIndx)

				# if count:
				# 	for key,val in business.iteritems():
				# 		print key, val
				# 	count = False

				attrVec[self.attrToIndx['stars']] = float(business['stars'])

				for attr, val in business['attributes'].iteritems():
					if type(val) == types.BooleanType: # TODO: non-bool/deeper attr
						attrVec[self.attrToIndx[attr]] = float(val)
					elif attr == 'Good For' or attr == 'Ambience':
						prefix = 'Good For ' if attr == 'Good For' else 'Ambience '
						for item in val:
							key = prefix + item
							attrVec[self.attrToIndx[key]] = float(val[item])
					elif attr == 'Price Range':
						attrVec[self.attrToIndx[attr]] = float(val)

				for category in business['categories']:
					if category != 'Restaurants':
						attrVec[self.attrToIndx[category]] = 1.0

				nid = util.getNId(business['business_id'])
				self.attrDict[util.getNId(business['business_id'])] = attrVec
		edgeIds = set([NI.GetId() for NI in self.G.Nodes()])
		bizIds = set(self.attrDict.keys())

	def __getAvgAttr(self, businesses):
		attrVecs = [np.array(self.attrDict[nid]) for nid in businesses]
		return np.average(attrVecs, axis=0)

	def __defaultScoreFn(self, dist):
		return math.exp(-dist)

	def getEdgeScore(self, edge, scoreFn=None):
		scoreFn = scoreFn or self.__defaultScoreFn
		userNIds = set(util.getUserBizNIds(self.G, self.attrDict.keys())[0])
		if edge[0] in userNIds:
			uid, bid = edge
		elif edge[1] in userNIds:
			bid, uid = edge
		else:
			exit('----------------------ERROR----------------------')

		UI = self.G.GetNI(uid)
		businesses = [UI.GetNbrNId(n) for n in xrange(UI.GetDeg())] # get reviewed businesses
		avgAttr = self.__getAvgAttr(businesses)
		dist = np.linalg.norm(avgAttr - np.array(self.attrDict[bid]))
		# compute the scores using the scoring function
		return scoreFn(dist)

	# Returns the top k recommendations for each user
	def getBusinessRecs(self, k, weightedMeans=False, weightedBusinesses=False, scoreFn=None, scoresFile='curated-data/scores.json'):
		scoreFn = scoreFn or self.__defaultScoreFn
		userNIds, businessNIds = util.getUserBizNIds(self.G, self.attrDict.keys())
		recs = {}
		for uid in userNIds:
			UI = self.G.GetNI(uid)
			businesses = [UI.GetNbrNId(n) for n in xrange(UI.GetDeg())] # get reviewed businesses
			avgAttr = self.__getAvgAttr(businesses)
			# print avgAttr
			bizScores = {}
			for bid in businessNIds:
				if bid not in businesses:
					dist = np.linalg.norm(avgAttr - np.array(self.attrDict[bid]))
					# compute the scores using the scoring function
					if scoreFn is not None:
						bizScores[bid] = scoreFn(dist)
					else:
						bizScores[bid] = self.score(dist)
			topKBIds = sorted(bizScores, key=bizScores.get, reverse=True)[:k]
			# normalize scores for a given user
			for bid in topKBIds:
				# recs[tuple(sorted((uid, bid)))] = bizScores[bid] / float(max(bizScores.values()))
				recs[tuple(sorted((uid, bid)))] = bizScores[bid]
		# print recs
		return recs


def main(argv):
	G = snap.LoadEdgeList(snap.PUNGraph, Const.review_edge_list, 0, 1)
	Recommender = BizBasedRecs(G)
	Recommender.getRecommendations(1)


if __name__ == '__main__': main(sys.argv)
