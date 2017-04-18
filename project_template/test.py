from .models import Docs
import os
import json
import numpy as np


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


##responds to request
def find_similar(query):
    query = query.lower() # business_name_to_id.json has all business names in lower case
    sim_matrix, unique_ids, business_id_to_name, business_name_to_id = read_file(1)
    bid = business_name_to_id[query][0]
    result = find_most_similar(sim_matrix, unique_ids, business_id_to_name, bid)

    return result 
