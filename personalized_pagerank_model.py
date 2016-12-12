
from collections import defaultdict
import random

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.preprocessing import normalize
import snap

from const import Const

class LinkPredictorModel(object):
	def __init__(self, G, alpha):
		self.G = G
		self.alpha = alpha

	def _getNbrNodeIds(self, nid, BG=False):
		if BG:
			node = self.BG.GetNI(nid)
		else:
			node = self.G.GetNI(nid)
		if not BG and node.GetOutDeg() > 0 and node.GetInDeg() > 0:
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

	def _setBGNodeMapping(self, GNId, BGNId):
		self.BGMapping['bg_'+str(BGNId)] = GNId
		self.BGMapping['g_'+str(GNId)] = BGNId

	def _getGNodeId(self, BGNId):
		return self.BGMapping['bg_'+str(BGNId)]

	def _getBGNodeId(self, GNId):
		return self.BGMapping['g_'+str(GNId)]

	def _getBusinessGraph(self):
		print 'Creating business-to-business graph'
		self.BG = snap.TUNGraph.New()
		self.BGMapping = {}
		i = 0
		for business_node in self.G.Nodes():
			if business_node.GetOutDeg() > 0: continue
			self.BG.AddNode(i)
			self._setBGNodeMapping(business_node.GetId(), i)
			i += 1

		self.weights = defaultdict(int)
		for business_node in self.BG.Nodes():
			for user_nid in self._getNbrNodeIds(self._getGNodeId(business_node.GetId())):
				for nbr_business_nid in self._getNbrNodeIds(user_nid):
					self.BG.AddEdge(business_node.GetId(), self._getBGNodeId(nbr_business_nid))
					self.weights[tuple(sorted((business_node.GetId(), self._getBGNodeId(nbr_business_nid))))] += 1
		print 'Done creating business-to-business graph'

	def _getExtendedSet(self, start_set, n):
		extended_set = set([self._getBGNodeId(nid) for nid in start_set])
		for _ in xrange(n):
			temp = set()
			for bgnid in extended_set:
				temp |= set(self._getNbrNodeIds(bgnid, True))
			extended_set |= temp
			print len(extended_set)
		return extended_set

	def _getQprime(self, extended_set):
		print 'Creating adjacency matrix'
		row = []
		col = []
		data = []
		for edge, weight in self.weights.iteritems():
			u, v = edge
			if not (u in extended_set and v in extended_set): continue
			row.append(u)
			row.append(v)
			col.append(v)
			col.append(u)
			data.append(weight)
			data.append(weight)
		self.Qprime = csr_matrix((data, (row,col)), shape=(self.BG.GetNodes(),self.BG.GetNodes()), dtype=np.float64)
		normalize(self.Qprime, norm='l1', axis=1, copy=False)
		print self.Qprime.count_nonzero()
		print 'Done creating adjacency matrix'

	def _getIncrementColMatrix(self, j, val):
		size = self.Qprime.get_shape()[0]
		row = range(size)
		col = [j]*size
		data = [val]*size
		return csr_matrix((data, (row,col)), shape=self.Qprime.get_shape())

	def _getQ(self, start_set):
		self.Q = self.Qprime * (1 - self.alpha)
		for bgnid in [self._getBGNodeId(nid) for nid in start_set]:
			self.Q += self._getIncrementColMatrix(bgnid, self.alpha)
		print self.Q.count_nonzero()

	def _powerIteration(self, n):
		size = self.Q.get_shape()[0]
		p = [1.0 / size]*size
		for i in xrange(n):
			print i
			self.Q *= self.Q
			p, p_old = self.Q * p , p
			if np.allclose(p, p_old): break
		return p

	def getBusinessRecs(self, k, user_nids, n_iters=500, powerIteration=False):
			recs = {}
			if powerIteration:
				self._getBusinessGraph()
			else:
				self.n_iters = n_iters
			# loop over user ids
			for user_nid in user_nids:
				start_set = self._getNbrNodeIds(user_nid)
				# get personalized pagerank scores
				if powerIteration:
					# get all businesses n hops away from start set
					extended_set = self._getExtendedSet(start_set, n=1)
					self._getQprime(extended_set) # get Q'
					self._getQ(start_set) # get Q

					p = self._powerIteration(5)
					scores = {self._getGNodeId(business_id): score for business_id, score in enumerate(p)}
				else:
					scores = defaultdict(float)
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
