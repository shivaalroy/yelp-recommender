"""
Evaluates a link prediction algorithm
"""

import numpy as np
import operator
import random
import snap
import sys
import util

from user_centroid_model import LinkPredictorModel
from const import Const


def deleteEdgeFromNode(graph, node):
	# TODO loop over shuffled nodes and delete edge when rating is above threshold
	nthNbr = int(random.random()*node.GetDeg())
	bizNId = node.GetNbrNId(nthNbr)
	edge = tuple(sorted((node.GetId(), bizNId)))
	graph.DelEdge(edge[0], edge[1])
	return edge


def main(argv):
	print 'Evaluating centroid-based, top-k link prediction'
	G = snap.LoadEdgeList(snap.PUNGraph, Const.review_edge_list, 0, 1)
	userNIds = list(util.getNIdDict(Const.review_mapping)[1])
	deletedEdges = set(deleteEdgeFromNode(G, G.GetNI(NId)) for NId in userNIds)
	recommender = LinkPredictorModel(G)

	recommendations = recommender.getBusinessRecs(k=10)
	print len(recommendations)
	diff = deletedEdges - set(recommendations)
	print len(diff)
	print 1 - 1.0 * len(diff) / len(deletedEdges)

	# for edge in deletedEdges:
	# 	print edge
	# 	print recommender.getEdgeScore(edge)


if __name__ == '__main__': main(sys.argv)
