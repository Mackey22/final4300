#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .models import Docs
import os
import json
import numpy as np
import Levenshtein
from collections import defaultdict
from helpers import sort_dict_by_val
import requests


#YELP API
app_id ='xGJw03IyUyyPy4XuNn4h_A'
app_secret = 'HfiPbyE1t1tzH7NkEJ5e1kcG157gw1uQ15BX4YhiQCpJjHyAR34T3AUuP1aU2nz9'
data = {'grant_type': 'client_credentials',
        'client_id': app_id,
        'client_secret': app_secret}
token = requests.post('https://api.yelp.com/oauth2/token', data=data)
access_token = token.json()['access_token']       
url = 'https://api.yelp.com/v3/businesses/search'
headers = {'Authorization': 'bearer %s' % access_token}


def api_business_info(business_name, location):
    params = {'location': location,
          'term': business_name,
         }
    url = 'https://api.yelp.com/v3/businesses/search'
    # url = 'https://api.yelp.com/v3/businesses/' + business_name + "-" + location + "/reviews"
    resp = requests.get(url=url, params=params, headers=headers)
    top_business = resp.json()['businesses'][0]
    return top_business



# k is number of results to display
def find_most_similar(topMatches, unique_ids, business_id_to_name, id1, destCity, k=5):
    """
    Find most similar restaurants to the given restaurant id.

    Accepts: similarity matrix of restauranst, restaurant id.
    Returns: list of (score, restaurant name) tuples for restaurant with id1 sorted by cosine_similarity score
    """
    #rel_index = unique_ids.index(id1)
    #rel_row = sim_matrix[rel_index]
    #print "rel_index: "
    #print rel_index
    #print "destCity: "
    #print destCity
    topMatchesRow = topMatches[id1][destCity]
    #max_indices = np.argpartition(rel_row, -k)[-k:]
    #most_similar_scores_and_ids = [(rel_row[x], business_id_to_name[unique_ids[x]]) for x in max_indices]
    #most_similar_scores_and_ids = sorted(most_similar_scores_and_ids,key=lambda x:-x[0])
    most_similar_ids = [business_id_to_name[x] for x in topMatchesRow][:k]
    # id -> (name,city,state)
    res = []
    for info in most_similar_ids:
        name = info[0]
        city = info[1]
        state = info[2]
        location = city + " " + state
        extra_info = api_business_info(name,location)
        res.append(extra_info)
    return res


    # return most_similar_scores_and_ids


def get_ordered_cities():
    data = read(1)["cities"]
    #Deal with Montréal and other accent problems here
    for i in range(len(data)):
        data[i] = data[i].replace(u'\xe9', 'e')
    return sorted(data[:10]), sorted(data)


def read(n):
    path = Docs.objects.get(id=n).address
    file = open(path)
    data = json.load(file)
    return data


def read_file(n):
    path = Docs.objects.get(id=n).address
    file = open(path)
    data = json.load(file)
    #sim_matrix = data['svd_matrix']
    topMatches = data['topMatches']
    unique_ids = data['unique_ids']
    business_id_to_name = data['business_id_to_name']
    business_name_to_id = data['business_name_to_id']
    #print "length sim matrix: " + str(len(sim_matrix))
    print "length unique_ids: " + str(len(unique_ids))
    print unique_ids[0]
    #print business_id_to_name[unique_ids[0]]
    return topMatches, unique_ids, business_id_to_name, business_name_to_id


# responds to request
def find_similar(query,origin,destination):
    print origin,destination
    origin = origin.lower()
    destination = destination.lower()
    query = query.lower() # business_name_to_id.json has all business names in lower case
    topMatches, unique_ids, business_id_to_name, business_name_to_id = read_file(1)
    if query in business_name_to_id:
        bid = business_name_to_id[query][0]
        lists = business_name_to_id[query]
        for i in range(len(lists[0])):
            if lists[1][i] == origin:
                bid = lists[0][i]
                break
        # This if/else block is to deal with the unique_ids problem. Remove it later on
        if bid in unique_ids:
            result = find_most_similar(topMatches, unique_ids, business_id_to_name, bid, destination)
        else:
            minDist = 999999
            # If query isn't in our business list, find match with lowest edit distance. Change later to choose correct one from list of values (same named restaurants, different cities)
            bestMatchKey = query
            bestMatchBid = ''
            for bid in unique_ids:
                business = business_id_to_name[bid]
                name = business[0]
                city = business[1] # Use this later to restrict search to within origin city. Not using it now because it'll suck with a small dataset
                dist = Levenshtein.distance(name, query)
                if dist < minDist:
                    minDist = dist
                    bestMatchKey = name
                    bestMatchBid = bid
            bid = bestMatchBid
            result = find_most_similar(topMatches, unique_ids, business_id_to_name, bid, destination)
    else:
        minDist = 999999
        # If query isn't in our business list, find match with lowest edit distance. Change later to choose correct one from list of values (same named restaurants, different cities)
        bestMatchKey = query
        bestMatchBid = ''
        for bid in unique_ids:
            business = business_id_to_name[bid]
            name = business[0]
            city = business[1] # Use this later to restrict search to within origin city. Not using it now because it'll suck with a small dataset
            dist = Levenshtein.distance(name, query)
            if dist < minDist:
                minDist = dist
                bestMatchKey = name
                bestMatchBid = bid
        # This code should work once we're using the complete dataset. But commented out and using simpler version for now for prototype
        # for key, value in business_name_to_id.iteritems():
        #     if origin in value[1]:
        #         idx = value[1].indexOf(origin)
        #         dist = Levenshtein.distance(query, key)
        #         if dist < minDist:
        #             minDist = dist
        #             bestMatchKey = key
        #             bestMatchBid = value[0][i]
        bid = bestMatchBid
        result = find_most_similar(topMatches, unique_ids, business_id_to_name, bid, destination)

    return result, bestMatchKey
