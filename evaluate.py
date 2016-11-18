"""
Evaluates a link-prediction algorithm
"""

import numpy as np
import operator
import random
import snap
import sys
import util

from biz_based_recs import BizBasedRecs
from const import Const


def deleteEdgeFromNode(graph, node):
	nthNbr = int(random.random()*node.GetDeg())
	bizNId = node.GetNbrNId(nthNbr)
	edge = tuple(sorted((node.GetId(), node.GetNbrNId(nthNbr))))
	graph.DelEdge(edge[0], edge[1])
	return edge


def main(argv):
	G = snap.LoadEdgeList(snap.PUNGraph, Const.review_edge_list, 0, 1)
	userNIds = list(util.getNIdDict(Const.review_mapping)[1])
	deletedEdges = set(deleteEdgeFromNode(G, G.GetNI(NId)) for NId in userNIds)
	recommender = BizBasedRecs(G)
	recommendations = recommender.getRecommendations(k=1)
	diff = deletedEdges - set(recommendations)
	print len(diff) / float(len(deletedEdges))


if __name__ == '__main__': main(sys.argv)
