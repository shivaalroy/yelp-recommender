# util.py

import csv

edgeListFile = "./curated-data/edge_list.json"
reviewsFile = "./curated-data/reviews.txt"

# Given a user or business id, hash and mod to get its node id
def getNId(id):
    return hash(id) % 100000

# Creates the edge list file of node ids for users and businesses
def createEdgeListFile():
    with open(reviewsFile, 'r') as readFile, open(edgeListFile, 'w') as writeFile:
        next(readFile) # skip heading
        reader = csv.reader(readFile, delimiter='\t')
        for userId, businessId in reader:
            writeFile.write(str(getNId(userId))+'\t'+str(getNId(businessId)))
            writeFile.write('\n')
    return edgeListFile
