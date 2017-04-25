import json
import numpy as np
from collections import defaultdict
# from data_play import make_hist
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import time
from collections import defaultdict
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
import sys

def sort_dict_by_val(d):
    """Get a list of a dict's keys ordered by descending values."""
    return sorted(d, key=d.__getitem__, reverse=True)

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


def get_reviews_and_ids(maxNum, minReviews):
    """Return list of unique business_ids, list of concatenated reviews corresponding to list of business_ids."""
    reviews_map = defaultdict(str)
    count = 0

    filteredBusinesses = 0
    print("\nIn get_reviews_and_ids")
    loadReviewsStart = time.time()
    with open('jsons/reviews.json') as data_file:
        data = json.load(data_file)
    loadReviewsEnd = time.time()
    print ("Loaded reviews in " + str(loadReviewsEnd - loadReviewsStart) + " seconds\n")
    #print("Number of businesses in file to iterate through: " + str(len(data)))
    reviewMapStart = time.time()
    for key in data:
        if int(data[key]['review_count']) >= minReviews:
            count += 1
            reviews_map[key] = data[key]['reviews']
            if count >= maxNum:
                break
        else:
            filteredBusinesses += 1
    reviewMapEnd = time.time()
    print ("Created review map in " + str(reviewMapEnd - reviewMapStart) + " seconds\n")
    print("Included " + str(count) + " businesses, filtered out " + str(filteredBusinesses) + " businesses with under " + str(minReviews) + " reviews")

    ordered_business_ids = []
    ordered_reviews = []

    orderedReviewsStart = time.time()
    for ID,reviews in reviews_map.iteritems():
        ordered_business_ids.append(ID)
        ordered_reviews.append(reviews)
    orderedReviewsEnd = time.time()
    print ("Ordered businesses & reviews in " + str(orderedReviewsEnd - orderedReviewsStart) + " seconds\n")
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


def lookup_business_id(name, city, state):
        with open('business_name_to_id.json') as data_file:
            business_name_to_id = json.load(data_file)
        ids = business_name_to_id[name]
        rest_id = ids[0]
        for i in range(len(ids[0])):
            if ids[1][i] == city and ids[2][i] == state:
                rest_id = ids[0][i]
                break
        #rest_id = ids[0] # For now, just assume the user means the 1st restaurant with that given name. Later, filter based on city to find the exact one
        return rest_id


def process_query(query, city, state, sim_matrix):
    query = query.lower() # business_name_to_id.json has all business names in lower case
    city = city.lower()
    state = state.lower()
    bid = lookup_business_id(query, city, state)
    most_sim = find_most_similar(sim_matrix, bid)
    return most_sim

# query = "mcdonald's"
# print "10 most similar restaurants to " + query + " are: \n"
# print process_query(query, sim_matrix)

def get_ordered_cities():
    cities = defaultdict(int)
    with open('yelpdata/yelp_academic_dataset_business.json') as data_file:
        for line in data_file:
            data = json.loads(line)
            cities[data['city']] += 1
    dests = sort_dict_by_val(cities)
    return dests

def gen_business_id_to_name(cutoff, minReviews):
    """Return Dict - maps business id to business name."""
    business_id_to_name = defaultdict(str)
    with open('yelpdata/yelp_academic_dataset_business.json') as data_file:
        count = 0
        for line in data_file:
            data = (json.loads(line))
            if int(data['review_count']) >= minReviews:
                count += 1
                business_id_to_name[data['business_id']] = (data['name'].lower(), data['city'].lower(), data['state'].lower())
                if count > cutoff:
                    break
    with open('business_id_to_name.json', 'w') as fp:
        json.dump(business_id_to_name, fp)


def gen_business_name_to_id(cutoff, minReviews):
    """Return Dict - maps business names to business ids."""
    business_name_to_id = defaultdict(str)
    with open('yelpdata/yelp_academic_dataset_business.json') as data_file:
        count = 0
        for line in data_file:
            data = (json.loads(line))
            if int(data['review_count']) >= minReviews:
                count += 1
                if data['name'].lower() in business_name_to_id:
                    business_name_to_id[data['name'].lower()][0].append(data['business_id'])
                    business_name_to_id[data['name'].lower()][1].append(data['city'].lower())
                    business_name_to_id[data['name'].lower()][2].append(data['state'].lower())
                else:
                    business_name_to_id[data['name'].lower()] = ([data['business_id']], [data['city'].lower()], [data['state'].lower()])
                if count > cutoff:
                    break
    with open('business_name_to_id.json', 'w') as fp:
        json.dump(business_name_to_id, fp)


def map_restaurant_to_top_similar(svd_matrix, unique_ids, business_id_to_name, numToFind):
    print "Creating map from city -> restaurant -> top sim restaurants"
    topRestStart = time.time()
    n, d = svd_matrix.shape
    topMatchMat = np.zeros((n, numToFind))
    for i in range(n):
        restaurant_to_mult = svd_matrix[i]
        one_restaurant_similarity = np.dot(svd_matrix, restaurant_to_mult)
        # print svd_matrix.shape, restaurant_to_mult.shape, one_restaurant_similarity.shape

        ordered_indices = np.argsort(one_restaurant_similarity)[::-1]
        # print "Indices", ordered_indices[0, :20]
        #print "Ordered Scores", one_restaurant_similarity[ordered_indices][1:numToFind+1]
        #print ordered_indices
        topMatchMat[i] = ordered_indices[1:numToFind+1]
    #print topMatchMat
    topRestEnd = time.time()
    print("Mapping restaurants to top similar took: " + str(topRestEnd - topRestStart) + " seconds\n")
    return topMatchMat


# Generates a single json file containing the similarity matrix, unique ids list mapping sim matrix index to corresponding business id, and business id to name/business name to id dicts
def gen_data_file():
    start = time.time()
    minReviews = 25  # Change this to change minimum number of business reviews for it to be included in dataset
    cutoff = 300 # Cut off at 300 businesses for size limitaitons, figure out later.
    gen_business_start = time.time()
    print("starting business id dict generation")
    gen_business_id_to_name(999999, minReviews) # I think we can't cut this off when we're only using a partial dataset
    gen_business_name_to_id(999999, minReviews)
    with open('business_id_to_name.json') as data_file:
        business_id_to_name = json.load(data_file)
    with open('business_name_to_id.json') as data_file:
        business_name_to_id = json.load(data_file)
    gen_business_end = time.time()
    print("finished business id dict generation in " + str(gen_business_end - gen_business_start) + " seconds\n")
    print("starting initial sim_mat generation")
    sim_mat_start = time.time()
    cities = get_ordered_cities()
    get_reviews_start = time.time()
    unique_ids, reviews = get_reviews_and_ids(cutoff, minReviews) # Also does filtering based on review count here
    get_reviews_end = time.time()
    print ("finished get_reviews_and_ids in " + str(get_reviews_end - get_reviews_start) + " seconds\n")
    n_feats = 5000
    tfidf_vec = TfidfVectorizer(max_df=0.8, min_df=.10, max_features=n_feats, stop_words='english', norm='l2')
    fit_transform_start = time.time()
    restaurant_by_vocab_matrix = tfidf_vec.fit_transform(reviews)
    fit_transform_end = time.time()
    print ("finished tfidf_vec.fit_transform in " + str(fit_transform_end - fit_transform_start) + " seconds\n")

    # Don't need this code when we're using SVD on the restaurant_by_vocab matrix
    # gen_sim_matrix_start = time.time()
    # sim_matrix = gen_sim_matrix(unique_ids, restaurant_by_vocab_matrix)
    # gen_sim_matrix_end = time.time()
    # print ("finished gen_sim_matrix in " + str(gen_sim_matrix_end - gen_sim_matrix_start) + " seconds\n")
    sim_mat_end = time.time()
    print ("finished initial sim_mat generation in " + str(sim_mat_end - sim_mat_start) + " seconds\n")

    # perform SVD
    svdStart = time.time()
    print ("starting SVD")
    reduced_size = 50 # Can by changed as needed
    lsa = TruncatedSVD(reduced_size, algorithm='randomized')
    svd_matrix = lsa.fit_transform(restaurant_by_vocab_matrix)
    svd_matrix = Normalizer(copy=False).fit_transform(svd_matrix) # copy=false to perform in place normalization, useful on larger dataset
    sim_matrix = svd_matrix.dot(svd_matrix.T)
    svdEnd = time.time()
    print ("finished SVD in " + str(svdEnd - svdStart) + " seconds\n")
    # end SVD

    topNToFind = 10 # Find top 10 most similar restaurants
    topMatches = map_restaurant_to_top_similar(svd_matrix, unique_ids, business_id_to_name, topNToFind)

    saveDataStart = time.time()

    data = {}
    data['business_id_to_name'] = business_id_to_name
    data['business_name_to_id'] = business_name_to_id
    data['topMatches'] = topMatches.tolist()
    data['unique_ids'] = unique_ids
    data['cities'] = cities

    with open('jsons/kardashian-transcripts.json', 'w') as fp:
        json.dump(data, fp)
    #with open('jsons/svd_matrix.json', 'w') as fp:
    #    json.dump(svd_matrix.tolist(), fp)

    saveDataEnd = time.time()
    print("Saving preprocessed data took " + str(saveDataEnd - saveDataStart) + " seconds\n")

    end = time.time()
    print("Preprocessing took: " + str(end - start) + " seconds")


def load_precomputed_svds():
    with open('jsons/kardashian-transcripts.json') as fp:
        data = json.load(fp)
    with open('business_id_to_name.json') as fp:
        business_id_to_name = json.load(fp)
    return np.array(data["svd_matrix"]), np.array(data['unique_ids']), business_id_to_name


if __name__ == "__main__":
    # print("before get_reviews_and_ids() call\n")
    # unique_ids, reviews = get_reviews_and_ids()
    # print("after get_reviews_and_ids() call\n")

    # print("length of unique_ids: " + str(len(unique_ids)))
    # n_feats = 5000
    # tfidf_vec = TfidfVectorizer(max_df=0.8, min_df=.10, max_features=n_feats, stop_words='english', norm='l2')
    # restaurant_by_vocab_matrix = tfidf_vec.fit_transform(reviews)

    gen_data_file() # Uncomment this to run preprocessing: Generates data file with sim matrix, business id/name dicts, and unique_ids for indexing business ids in sim matrix
    #mtx, unique_ids, business_id_to_name = load_precomputed_svds()
    #topNToFind = 10 # Find top 10 most similar restaurants
    #map_restaurant_to_top_similar(mtx, unique_ids, business_id_to_name, topNToFind)
