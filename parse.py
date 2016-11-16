"""
Extracts features for restaurant businesses in the Yelp Challenge Dataset
"""

import sys
from json import loads
from json import dumps
from re import sub

def parsebusiness(json_file):
    businesses = []
    with open(json_file, 'r') as f:
        for line in f:
            businesses.append(loads(line))
    print 'Total businesses before', len(businesses)

    data = []
    businessids = set()
    for business in businesses:
        if ('Restaurants' in business['categories']) and (business['city'] == 'Las Vegas'):
            data.append(business)
            businessids.add(business['business_id'])

    print 'Total Restaurants: ', len(data)
    data_file = open('yelp_data/restaurant_data.json','w')
    for business in data:
        data_file.write(dumps(business, data_file))
        data_file.write('\n')
    return businessids

def parsereview(json_file, businessids):
    reviews = []
    edges = []
    with open(json_file, 'r') as f:
        for line in f:
            reviews.append(loads(line))
    print 'Total reviews before', len(reviews)

    data = []
    userids = set()
    for review in reviews:
        if review['business_id'] in businessids:
            data.append(review)
            userids.add(review['user_id'])
            edges.append(str(review['user_id'])+' '+str(review['business_id'])+'\n')

    print 'Total Reviews: ', len(data)
    data_file = open('yelp_data/review_data.json','w')
    for review in data:
        data_file.write(dumps(review, data_file))
        data_file.write('\n')
    edges_file = open('yelp_data/reviews.txt','w')
    for edge in edges:
        edges_file.write(edge)
    return userids

def parseuser(json_file, userids):
    users = []
    edges = []
    with open(json_file, 'r') as f:
        for line in f:
            users.append(loads(line))

    print 'Total users before', len(users)
    data = []
    for user in users:
        if user['user_id'] in userids:
            data.append(user)
            for friend in user['friends']:
                if user['user_id'] < friend:
                    edges.append(user['user_id']+' '+friend+'\n')

    print 'Total Users: ', len(data)
    data_file = open('yelp_data/user_data.json','w')
    for user in data:
        data_file.write(dumps(user, data_file))
        data_file.write('\n')
    edges_file = open('yelp_data/friends.txt','w')
    for edge in edges:
        edges_file.write(edge)

def main(argv):
    f = 'yelp-data/yelp_academic_dataset_business.json'
    businessids = parsebusiness(f)
    print 'Success parsing ' + f
    f2 = 'yelp-data/yelp_academic_dataset_review.json'
    userids = parsereview(f2, businessids)
    print 'Success parsing', f2
    f3 = 'yelp-data/yelp_academic_dataset_user.json'
    parseuser(f3, userids)
    print 'Success parsing', f3

if __name__ == '__main__':
    main(sys.argv)
