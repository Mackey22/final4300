#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .models import Docs
import os
import json
import Levenshtein
from collections import defaultdict
from helpers import sort_dict_by_val
import requests
import time
import grequests


# YELP API
app_id = 'xGJw03IyUyyPy4XuNn4h_A'
app_secret = 'HfiPbyE1t1tzH7NkEJ5e1kcG157gw1uQ15BX4YhiQCpJjHyAR34T3AUuP1aU2nz9'
data = {'grant_type': 'client_credentials',
        'client_id': app_id,
        'client_secret': app_secret}
token = requests.post('https://api.yelp.com/oauth2/token', data=data)
access_token = token.json()['access_token']
url = 'https://api.yelp.com/v3/businesses/search'
headers = {'Authorization': 'bearer %s' % access_token}


def build_request(business_name, location):
    params = {'location': location, 'term': business_name}
    url = 'https://api.yelp.com/v3/businesses/search'
    return grequests.get(url=url, params=params, headers=headers)


def process_response(resp, business_name, location):
    response_time = time.time()
    try:
        top_businesses = resp.json()['businesses']
        for i in range(len(top_businesses)):
            b1 = (top_businesses[i]['name']).lower()
            b2 = business_name.lower()
            a1 = (top_businesses[i]['location']['address1']).lower()
            a2 = location.lower()

            # immediately return business with 2 matches
            if (b1 == b2) and (a1 == a2):
                return top_businesses[i]
            # save business with one match
            if (b1 == b2) or (a1 == a2):
                tmp = top_businesses[i]
        # return business with one match
        print "response time is", time.time() - response_time, "seconds"
        return tmp

    except:
        print "response time is", time.time() - response_time, "seconds"
        return []


# k is number of results to display
def find_most_similar(topMatches, unique_ids, business_id_to_name, id1, destCity, contributing_words, k=15):
    """
    Find most similar restaurants to the given restaurant id.

    Accepts: similarity matrix of restauranst, restaurant id.
    Returns: list of (score, restaurant name) tuples for restaurant with id1 sorted by cosine_similarity score
    """
    topMatchesRow = topMatches[id1][destCity]
    # max_indices = np.argpartition(rel_row, -k)[-k:]
    # most_similar_scores_and_ids = [(rel_row[x], business_id_to_name[unique_ids[x]]) for x in max_indices]
    # most_similar_scores_and_ids = sorted(most_similar_scores_and_ids,key=lambda x:-x[0])
    most_similar_ids = [business_id_to_name[x] for x in topMatchesRow][:k]
    # id -> (name,city,state)
    names = []
    adds = []

    res2 = []
    reqs = []
    api_time = time.time()
    for i in range(len(most_similar_ids)):
        info = most_similar_ids[i]
        name = info[0]
<<<<<<< HEAD
        full_address = info[3]
        names.append(name)
        adds.append(full_address)
        res2.append(contributing_words[topMatchesRow[i]])

        request = build_request(name, full_address)
        reqs.append(request)
    print "Building requests takes", time.time() - api_time, "seconds"
    print reqs

    make_requests_time = time.time()
    results = grequests.imap(reqs)
    print "map time was", time.time() - make_requests_time, "seconds"
    print results
    res = [process_response(extra, names[i], adds[i]) for i, extra in enumerate(results) if extra != []]
    print res
    print "Making requests takes", time.time() - make_requests_time, "seconds"

    return res, res2


def get_ordered_cities():
    t = time.time()
    data = read(1)["cities"]
    print "Opened data in ", time.time() - t, "seconds"
    # Deal with Montréal and other accent problems here
    for i in range(len(data)):
        data[i] = data[i].replace(u'\xe9', 'e')
    print "Got ordered cities in", time.time() - t, "seconds"
    return sorted(data[:10]), (["Search in all cities"] + sorted(data))


def read(n):
    path = Docs.objects.get(id=n).address
    file = open(path)
    data = json.load(file)
    return data


def read_file(n):
    path = Docs.objects.get(id=n).address
    file = open(path)
    data = json.load(file)
    # sim_matrix = data['svd_matrix']
    topMatches = data['topMatches']
    unique_ids = data['unique_ids']
    business_id_to_name = data['business_id_to_name']
    business_name_to_id = data['business_name_to_id']
    contributing_words = data['contributing_words']
    autocomplete_info = data['autocomplete_info']

    return topMatches, unique_ids, business_id_to_name, business_name_to_id, contributing_words, autocomplete_info


# responds to request
def find_similar(query,origin,destination):
    print origin,destination
    origin = origin.lower()
    destination = destination.lower()
    query = query.lower() # business_name_to_id.json has all business names in lower case
    read_2 = time.time()
    topMatches, unique_ids, business_id_to_name, business_name_to_id, contributing_words, autocomplete_info = read_file(1)
    print "Loaded file in", time.time() - read_2, "seconds"
    bestMatchKey = ''
    search_timer = time.time()
    if query in business_name_to_id:
        print query
        bid = business_name_to_id[query][0]
        print bid
        lists = business_name_to_id[query]
        for i in range(len(lists[0])):
            if lists[1][i] == origin:
                bid = lists[0][i]
                break
        print "generating ish in", time.time() - search_timer, "seconds"
        result, result2 = find_most_similar(topMatches, unique_ids, business_id_to_name, bid, destination, contributing_words[bid])
    else:
        raise ValueError('query is not in business_name_to_id. This means that our unique_ids, autocomplete file, or results are not all aligned.')

    print "searched in", time.time() - search_timer, "seconds"
    return result, bestMatchKey, result2, autocomplete_info
