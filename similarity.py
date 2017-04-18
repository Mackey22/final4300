import json
import numpy as np
from collections import defaultdict
# from data_play import make_hist
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import time
from collections import defaultdict


def gen_business_id_to_name():
    """Return Dict - maps business id to business name."""
    business_id_to_name = defaultdict(str)
    # with open('yelp_academic_dataset_business.json') as data_file:
    #     for line in data_file:
    #         data = (json.loads(line))
    #         business_id_to_name[data['business_id']] = data['name']
    with open('business_id_to_name.json') as data_file:
        business_id_to_name = json.load(data_file)
    return business_id_to_name

# business_id_to_name = gen_business_id_to_name()

# Old version of the function parses the original Yelp dataset file
# def get_reviews_and_ids_old():
#     """Return list of unique business_ids, list of concatanted reviews corresponding to list of business_ids."""
#     reviews_map = defaultdict(str)
#     count = 0
#     with open('yelp_data/yelp_academic_dataset_review.json') as data_file:
#         for line in data_file:
#             # currently limits size as it won't run on my machine otherwise
#             # might speed it up to use .join instead, but I think mackey has code for this portion already anyway
#             if count < 2000:
#                 data = (json.loads(line))
#                 reviews_map[data['business_id']] += data['text']
#             count += 1

#     ordered_business_ids = []
#     ordered_reviews = []

#     for ID,reviews in reviews_map.iteritems():
#         ordered_business_ids.append(ID)
#         ordered_reviews.append(reviews)
#     print ordered_reviews[0]
#     return ordered_business_ids, ordered_reviews


def get_reviews_and_ids(maxNum):
    """Return list of unique business_ids, list of concatenated reviews corresponding to list of business_ids."""
    reviews_map = defaultdict(str)
    count = 0
    with open('reviews.json') as data_file:
        data = json.load(data_file)
    #print("Number of businesses in file to iterate through: " + str(len(data)))
    for key in data:
        count += 1
        reviews_map[key] = data[key]['reviews']
        if count > maxNum:
            break

    ordered_business_ids = []
    ordered_reviews = []

    for ID,reviews in reviews_map.iteritems():
        ordered_business_ids.append(ID)
        ordered_reviews.append(reviews)
    # print ordered_reviews[0]
    return ordered_business_ids, ordered_reviews


def prune_json(n):
    new_map = {}
    with open('jsons/try1.json') as data_file:
        data = json.load(data_file)
    for k, v in data.items():
        if v['review_count'] >= n:
            new_map[k] = v
    with open('jsons/pruned.json', 'w') as fp:
        json.dump(new_map, fp, indent=4)


def get_sim(vec1, vec2):
    """
    Get similarity of the two vectors.

    Arguments:
        name1: vector of the first city
        name2: vector of the second city
    Returns:
        similarity: Cosine similarity of the two sets of compiled restaurant reviews.
    """
    sim = cosine_similarity(vec1,vec2)
    return sim[0][0]


def gen_sim_matrix(unique_ids, restaurant_by_vocab_matrix):
    restaurant_sims = np.empty([len(unique_ids), len(unique_ids)], dtype=np.float32)
    for i in range(len(unique_ids)):
        for j in range(len(unique_ids)):
            if i != j:
                restaurant_sims[i][j] = get_sim(restaurant_by_vocab_matrix[i], restaurant_by_vocab_matrix[j])
            else:
                restaurant_sims[i][j] = 0
    return restaurant_sims


# print("About to generate sim matrix\n")
# sim_matrix = gen_sim_matrix(unique_ids, restaurant_by_vocab_matrix)
# print("Generated sim matrix\n")


def find_most_similar(sim_matrix, id1, k=10):
    """
    Find most similar restaurants to the given restaurant id.

    Accepts: similarity matrix of restauranst, restaurant id.
    Returns: list of (score, restaurant name) tuples for restaurant with id1 sorted by cosine_similarity score
    """
    rel_index = unique_ids.index(id1)
    rel_row = sim_matrix[rel_index]
    max_indices = np.argpartition(rel_row, -k)[-k:]
    most_similar_scores_and_ids = [(rel_row[x], business_id_to_name[unique_ids[x]]) for x in max_indices]
    print most_similar_scores_and_ids
    most_similar_scores_and_ids = sorted(most_similar_scores_and_ids,key=lambda x:-x[0])

    return most_similar_scores_and_ids


def lookup_business_id(name):
        with open('business_name_to_id.json') as data_file:
            business_name_to_id = json.load(data_file)
        ids = business_name_to_id[name]
        rest_id = ids[0] # For now, just assume the user means the 1st restaurant with that given name. Later, filter based on city to find the exact one
        return rest_id


def process_query(query, sim_matrix):
    query = query.lower() # business_name_to_id.json has all business names in lower case
    bid = lookup_business_id(query)
    most_sim = find_most_similar(sim_matrix, bid)
    return most_sim

# query = "mcdonald's"
# print "10 most similar restaurants to " + query + " are: \n"
# print process_query(query, sim_matrix)


# Generates a single json file containing the similarity matrix, unique ids list mapping sim matrix index to corresponding business id, and business id to name/business name to id dicts
def gen_data_file():
    start = time.time()
    with open('business_id_to_name.json') as data_file:
        business_id_to_name = json.load(data_file)
    with open('business_name_to_id.json') as data_file:
        business_name_to_id = json.load(data_file)
    unique_ids, reviews = get_reviews_and_ids(300)             # Cut off at 3000 businesses for size limitaitons, figure out later
    n_feats = 5000
    tfidf_vec = TfidfVectorizer(max_df=0.8, min_df=.10, max_features=n_feats, stop_words='english', norm='l2')
    restaurant_by_vocab_matrix = tfidf_vec.fit_transform(reviews)
    sim_matrix = gen_sim_matrix(unique_ids, restaurant_by_vocab_matrix)
    data = {}
    data['business_id_to_name'] = business_id_to_name
    data['business_name_to_id'] = business_name_to_id
    data['sim_matrix'] = sim_matrix.tolist()
    data['unique_ids'] = unique_ids
    with open('jsons/kardashian-transcripts.json', 'w') as fp:
        json.dump(data, fp)

    end = time.time()
    print("Preprocessing took: " + str(end - start) + " seconds")


if __name__ == "__main__":
    # print("before get_reviews_and_ids() call\n")
    # unique_ids, reviews = get_reviews_and_ids()
    # print("after get_reviews_and_ids() call\n")

    # print("length of unique_ids: " + str(len(unique_ids)))
    # n_feats = 5000
    # tfidf_vec = TfidfVectorizer(max_df=0.8, min_df=.10, max_features=n_feats, stop_words='english', norm='l2')
    # restaurant_by_vocab_matrix = tfidf_vec.fit_transform(reviews)

    gen_data_file() # Uncomment this to run preprocessing: Generates data file with sim matrix, business id/name dicts, and unique_ids for indexing business ids in sim matrix
