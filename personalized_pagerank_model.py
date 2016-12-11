
from collections import defaultdict
import random

import snap

from const import Const

class LinkPredictorModel(object):
	def __init__(self, G, user_nids, n_iters, alpha):
		self.G = G
		self.user_nids = user_nids
		self.n_iters = n_iters
		self.alpha = alpha
		# print 'Running with n_iters=%d, alpha=%f' % (n_iters, alpha)

	def _getNbrNodeIds(self, nid):
		node = self.G.GetNI(nid)
		if node.GetOutDeg() > 0 and node.GetInDeg() > 0:
			print 'nid=%d outdeg=%d, indeg=%d' % (nid, node.GetOutDeg(), node.GetInDeg())
		return [node.GetNbrNId(nbr) for nbr in xrange(node.GetDeg())]

	def _getPagerankScores(self, start_set, scores):
		business_nid = random.sample(start_set, 1)[0]
		for _ in xrange(self.n_iters):
			user_nid = random.sample(self._getNbrNodeIds(business_nid), 1)[0]
			business_nid = random.sample(self._getNbrNodeIds(user_nid), 1)[0]
			scores[business_nid] += 1
			if random.random() < self.alpha:
				business_nid = random.sample(start_set, 1)[0]

		for business_nid in start_set:
			scores[business_nid] = 0

		total = sum(scores.itervalues())
		scores = {k: v/total for k,v in scores.iteritems()}

		if abs(sum(scores.itervalues()) - 1) > 1e9:
			print 'PROBABILITY IS BROKEN', sum(scores.itervalues())

	def getBusinessRecs(self, k):
		recs = {}
		# loop over user ids
		for user_nid in self.user_nids:
			start_set = self._getNbrNodeIds(user_nid)
			scores = defaultdict(float)
			# get personalized pagerank scores
			self._getPagerankScores(start_set, scores)
			# add top k predictions to recommendations dictionary
			topKBusinessNIds = sorted(scores, key=scores.get, reverse=True)[:k]
			for business_nid in topKBusinessNIds:
				recs[tuple(sorted((user_nid, business_nid)))] = scores[business_nid]
		# print 'Returning k=%d recommendations per user' % k
		return recs


def main():
	G = snap.LoadEdgeList(snap.PNGraph, Const.review_edge_list, 0, 1)
	recommender = LinkPredictorModel(G)
	recommender.getBusinessRecs(10)


if __name__ == '__main__': main()
