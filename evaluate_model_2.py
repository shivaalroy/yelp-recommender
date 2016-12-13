"""
Evaluates the personalized pagerank link prediction algorithm
"""

import numpy as np
import random

import snap

from personalized_pagerank_model import LinkPredictorModel
from const import Const
import util


def deleteEdgeFromNode(graph, node):
	nthNbr = int(random.random()*node.GetOutDeg())
	bizNId = node.GetOutNId(nthNbr)
	edge = tuple(sorted((node.GetId(), bizNId)))
	graph.DelEdge(edge[0], edge[1])
	return edge


def main():
	print 'Evaluating pagerank-based, top-k link prediction'
	G = snap.LoadEdgeList(snap.PNGraph, Const.review_edge_list, 0, 1)
	userNIds = list(util.getUserNIdDict(Const.review_mapping))
	deletedEdges = set(deleteEdgeFromNode(G, G.GetNI(NId)) for NId in userNIds)

	# n_iters_range = [500, 1000, 2000, 5000]
	# alpha_range = [0.1, 0.2, 0.3, 0.4, 0.5]
	# grid = {}
	# for n_iters in n_iters_range:
	# 	for alpha in alpha_range:
	# 		print 'Running with n_iters=%d, alpha=%f' % (n_iters, alpha)
	# 		accuracies = []
	# 		for _ in xrange(50):
	# 			recommender = LinkPredictorModel(G, alpha)
	# 			recommendations = recommender.getBusinessRecs(10, userNIds, n_iters=n_iters)
	# 			diff = deletedEdges - set(recommendations)
	# 			accuracy = 1 - 1.0 * len(diff) / len(deletedEdges)
	# 			accuracies.append(accuracy)
	# 		grid[(n_iters,alpha)] = np.average(accuracies)
	# 		print np.average(accuracies)
	# print grid

	alpha_range = [0.3, 0.1, 0.5, 0.2, 0.4]
	for alpha in alpha_range:
		print 'Running with power iteration and alpha=%f' % alpha
		recommender = LinkPredictorModel(G, alpha=alpha)
		recommendations = recommender.getBusinessRecs(10, userNIds, powerIteration=True)
		diff = deletedEdges - set(recommendations)
		accuracy = 1 - 1.0 * len(diff) / len(deletedEdges)
		print accuracy


if __name__ == '__main__': main()
