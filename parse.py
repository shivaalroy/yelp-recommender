"""
Extracts features for restaurant businesses in the Yelp Challenge Dataset
"""

import sys
from json import loads
from json import dumps
from re import sub
import random

def parsebusiness(json_file, numBusinesses=100):
    data = []
    localeIds = set()
    with open(json_file, 'r') as f:
        for line in f:
            business = loads(line)
            if ('Restaurants' in business['categories']) and (business['city'] == 'Las Vegas'):
                data.append(business)
                localeIds.add(business['business_id'])
    print 'Total Restaurants: ', len(data)

    sampled_data = random.sample(data, numBusinesses)
    print 'Shrunk it to:', len(sampled_data)

    businessids = set()
    for business in sampled_data:
        businessids.add(business['business_id'])

    with open('curated-data/restaurant_data.json','w') as data_file:
        for business in sampled_data:
            data_file.write(dumps(business, data_file))
            data_file.write('\n')
    return businessids, localeIds

def filterLocaleReviews(json_file, localeIds):
    lineCount = 0
    with open(json_file, 'r') as readFile, open('yelp-data/las_vegas_reviews.json', 'w') as writeFile:
        for line in readFile:
            review = loads(line)
            if review['business_id'] in localeIds:
                writeFile.write(dumps(review))
                writeFile.write('\n')
                lineCount += 1
    print 'Las Vegas reviews:', lineCount


def parsereview(json_file, businessids):
    data = []
    edges = []
    userids = set()
    with open(json_file, 'r') as f:
        for line in f:
            review = loads(line)
            if review['business_id'] in businessids:
                data.append(review)
                edges.append(str(review['user_id'])+'\t'+str(review['business_id']))
                userids.add(review['user_id'])
    print 'Total Reviews:', len(data)

    with open('curated-data/review_data.json','w') as data_file:
        for review in data:
            data_file.write(dumps(review, data_file))
            data_file.write('\n')
    with open('curated-data/reviews.txt','w') as edges_file:
        edges_file.write('#user_id\tbusiness_id\n')
        for edge in edges:
            edges_file.write(edge)
            edges_file.write('\n')
    return userids

def parseuser(json_file, userids):
    data = []
    edges = []
    with open(json_file, 'r') as f:
        for line in f:
            user = loads(line)
            if user['user_id'] in userids:
                data.append(user)
                for friend in user['friends']:
                    if user['user_id'] < friend:
                        edges.append(user['user_id']+'\t'+friend)
    print 'Total Users:', len(data)

    with open('curated-data/user_data.json','w') as data_file:
        for user in data:
            data_file.write(dumps(user, data_file))
            data_file.write('\n')
    with open('curated-data/friends.txt','w') as edges_file:
        edges_file.write('#user_id\tfriend\n')
        for edge in edges:
            edges_file.write(edge)
            edges_file.write('\n')

def main(argv):
    f = 'yelp-data/yelp_academic_dataset_business.json'
    print 'Parsing ' + f
    businessids, localeIds = parsebusiness(f, 100)
    print 'Done parsing ' + f
    f2 = 'yelp-data/las_vegas_reviews.json'
    print 'Parsing ' + f2
    userids = parsereview(f2, businessids)
    print 'Done parsing', f2
    f3 = 'yelp-data/yelp_academic_dataset_user.json'
    print 'Parsing ' + f3
    parseuser(f3, userids)
    print 'Done parsing', f3
    # filterLocaleReviews(f2, localeIds)

if __name__ == '__main__':
    main(sys.argv)
