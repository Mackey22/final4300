from .models import Docs
import os
import json
import numpy as np
import Levenshtein
from collections import defaultdict
from helpers import sort_dict_by_val


def find_most_similar(sim_matrix, unique_ids, business_id_to_name, id1, k=5):
    """
    Find most similar restaurants to the given restaurant id.

    Accepts: similarity matrix of restauranst, restaurant id.
    Returns: list of (score, restaurant name) tuples for restaurant with id1 sorted by cosine_similarity score
    """
    rel_index = unique_ids.index(id1)
    rel_row = sim_matrix[rel_index]
    max_indices = np.argpartition(rel_row, -k)[-k:]
    most_similar_scores_and_ids = [(rel_row[x], business_id_to_name[unique_ids[x]]) for x in max_indices]
    most_similar_scores_and_ids = sorted(most_similar_scores_and_ids,key=lambda x:-x[0])

    return most_similar_scores_and_ids


def get_ordered_cities():
    data = read(1)["cities"]
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
    sim_matrix = data['sim_matrix']
    unique_ids = data['unique_ids']
    business_id_to_name = data['business_id_to_name']
    business_name_to_id = data['business_name_to_id']
    print "length sim matrix: " + str(len(sim_matrix))
    print "length unique_ids: " + str(len(unique_ids))
    print unique_ids[0]
    #print business_id_to_name[unique_ids[0]]
    return sim_matrix, unique_ids, business_id_to_name, business_name_to_id


# responds to request
def find_similar(query,origin,destination):
    print origin,destination
    originCity = origin.lower()
    destCity = destination.lower()
    query = query.lower() # business_name_to_id.json has all business names in lower case
    sim_matrix, unique_ids, business_id_to_name, business_name_to_id = read_file(1)
    if query in business_name_to_id:
        bid = business_name_to_id[query][0]
        lists = business_name_to_id[query]
        for i in range(len(lists[0])):
            if lists[1][i] == originCity:
                bid = lists[0][i]
                break
        result = find_most_similar(sim_matrix, unique_ids, business_id_to_name, bid)
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
        #     if originCity in value[1]:
        #         idx = value[1].indexOf(originCity)
        #         dist = Levenshtein.distance(query, key)
        #         if dist < minDist:
        #             minDist = dist
        #             bestMatchKey = key
        #             bestMatchBid = value[0][i]
        bid = bestMatchBid
        result = find_most_similar(sim_matrix, unique_ids, business_id_to_name, bid)

    return result, bestMatch
