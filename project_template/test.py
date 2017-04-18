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
    print business_id_to_name[unique_ids[0]]
    return sim_matrix, unique_ids, business_id_to_name, business_name_to_id


def get_ordered_cities():
    cities = defaultdict(int)
    with open('yelp_data/yelp_academic_dataset_business.json') as data_file:
        for line in data_file:
            data = json.loads(line)
            cities[data['city']] += 1
    dests = sort_dict_by_val(cities)[:10]

    dests = sorted(dests)
    homes = sorted(cities.keys())
    return dests, homes


# responds to request
def find_similar(query,origin,destination):
    print origin,destination
    query = query.lower() # business_name_to_id.json has all business names in lower case
    sim_matrix, unique_ids, business_id_to_name, business_name_to_id = read_file(1)
    if query in business_name_to_id:
        bid = business_name_to_id[query][0] # Change the index to find the correct restaurant based on city later.
    else:
        minDist = 999999
        # If query isn't in our business list, find match with lowest edit distance. Change later to choose correct one from list of values (same named restaurants, different cities)
        bestMatch = query
        for key, value in business_name_to_id.iteritems():
            dist = Levenshtein.distance(query, key)
            if dist < minDist:
                minDist = dist
                bestMatch = key
        bid = business_name_to_id[bestMatch][0]
    result = find_most_similar(sim_matrix, unique_ids, business_id_to_name, bid)

    return result, bestMatch
