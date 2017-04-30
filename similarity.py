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


def get_reviews_and_ids(maxNum, minReviews, business_id_to_name):
	"""Return list of unique business_ids, list of concatenated reviews corresponding to list of business_ids."""
	reviews_map = defaultdict(str)
	count = 0

	filteredBusinesses = 0
	print("\nIn get_reviews_and_ids")
	loadReviewsStart = time.time()
	with open('jsons/restaurant_categories.json') as data_file:
		valid_categories = set(json.load(data_file))
	#print("Number of businesses in file to iterate through: " + str(len(data)))
	reviewMapStart = time.time()
	category_map = {}
	with open('jsons/reviews.json') as data_file:
		data = json.load(data_file)
	loadReviewsEnd = time.time()
	print ("Loaded reviews in " + str(loadReviewsEnd - loadReviewsStart) + " seconds\n")
	badCategoryResults = 0
	duplicateNameCounts = 0
	for key in data:
		# Instead of checking conditions for the business again, just see if it is in business_id_to_name dict, where the conditions were already checked
		if key in business_id_to_name:
			count += 1
			reviews_map[key] = data[key]['reviews']
			category_map[key] = data[key]['data']['categories']
		else:
			filteredBusinesses += 1
		if count >= maxNum:
			break
		# badCategory = False 		# Keep track of if a non-food category was found
		# if int(data[key]['review_count']) >= minReviews:
		# 	if data[key]['data']['categories'] != None:
		# 		for category in data[key]['data']['categories']:
		# 			if category not in valid_categories:
		# 				badCategory = True
		# 				break
		# 		if not badCategory:
		# 			count += 1
		# 			reviews_map[key] = data[key]['reviews']
		# 			category_map[key] = data[key]['data']['categories']
		# 		else:
		# 			badCategoryResults += 1
		# 	if count >= maxNum:
		# 		break
		# else:
		# 	filteredBusinesses += 1

	reviewMapEnd = time.time()
	print ("Created review map in " + str(reviewMapEnd - reviewMapStart) + " seconds\n")
	print("Included " + str(count) + " businesses")
	print("Filtered out " + str(filteredBusinesses) + " businesses with under " + str(minReviews) + " reviews")
	print("Filtered out " + str(badCategoryResults) + " businesses that had non-food categories")

	ordered_business_ids = []
	ordered_reviews = []
	ordered_business_categories = []

	orderedReviewsStart = time.time()
	for ID,reviews in reviews_map.iteritems():
		ordered_business_ids.append(ID)
		ordered_reviews.append(reviews)
		ordered_business_categories.append(category_map[ID])
	orderedReviewsEnd = time.time()
	print ("Ordered businesses & reviews in " + str(orderedReviewsEnd - orderedReviewsStart) + " seconds\n")
	return ordered_business_ids, ordered_reviews, ordered_business_categories


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
	with open('jsons/restaurant_categories.json') as data_file:
		valid_categories = set(json.load(data_file))
	business_id_to_name = defaultdict(str)
	with open('yelpdata/yelp_academic_dataset_business.json') as data_file:
		count = 0
		for line in data_file:
			badCategory = False
			data = (json.loads(line))
			if int(data['review_count']) >= minReviews:
				if data['categories'] != None:
					for category in data['categories']:
						if category not in valid_categories:
							badCategory = True
							break
					if not badCategory:
						business_id_to_name[data['business_id']] = (data['name'].lower(), data['city'].lower(), data['state'].lower())
						count += 1
						if count > cutoff:
							break
	with open('business_id_to_name.json', 'w') as fp:
		json.dump(business_id_to_name, fp)


def gen_business_name_to_id(cutoff, minReviews):
	"""Return Dict - maps business names to business ids."""
	with open('jsons/restaurant_categories.json') as data_file:
		valid_categories = set(json.load(data_file))
	business_name_to_id = defaultdict(str)
	with open('yelpdata/yelp_academic_dataset_business.json') as data_file:
		count = 0
		for line in data_file:
			data = (json.loads(line))
			badCategory = False
			if int(data['review_count']) >= minReviews:
				if data['categories'] != None:
					for category in data['categories']:
						if category not in valid_categories:
							badCategory = True
							break
					if not badCategory:
						if data['name'].lower() in business_name_to_id:
							business_name_to_id[data['name'].lower()][0].append(data['business_id'])
							business_name_to_id[data['name'].lower()][1].append(data['city'].lower())
							business_name_to_id[data['name'].lower()][2].append(data['state'].lower())
						else:
							business_name_to_id[data['name'].lower()] = ([data['business_id']], [data['city'].lower()], [data['state'].lower()])
						count += 1
						if count > cutoff:
							break
	with open('business_name_to_id.json', 'w') as fp:
		json.dump(business_name_to_id, fp)

# Have to update this to do it based on dest city
def map_restaurant_to_top_similar(restaurant_by_vocab_matrix, unique_ids, business_id_to_name, numToFind):
	print "Creating map from city -> restaurant -> top sim restaurants"
	destCities = ['charlotte', 'henderson', 'las vegas', 'mesa', 'montreal', 'phoenix', 'pittsburgh', 'scottsdale', 'tempe', 'toronto']
	topMatchDict = {}
	topRestStart = time.time()
	n, d = restaurant_by_vocab_matrix.shape
	topMatchMat = np.zeros((n, numToFind), dtype=int)
	numDone = 0
	for i in range(n):
		topMatchDict[unique_ids[i]] = {}
		for city in destCities:
			topMatchDict[unique_ids[i]][city] = []
		dictItems = 0 # So we can break when dict has all the necessary entries for a restaurant
		restaurant_to_mult = restaurant_by_vocab_matrix[i]
		one_restaurant_similarity = np.dot(restaurant_by_vocab_matrix, restaurant_to_mult.T)
		fixedList = (one_restaurant_similarity.toarray()).flatten()
		ordered_indices = np.argsort(fixedList)
		for idx in ordered_indices:
			city = business_id_to_name[unique_ids[idx]][1]
			if city in topMatchDict[unique_ids[i]] and len(topMatchDict[unique_ids[i]][city])<numToFind:
				topMatchDict[unique_ids[i]][city].append(unique_ids[idx])
				dictItems += 1
				if dictItems >= numToFind*len(destCities):
					break
		numDone += 1
		#print(business_id_to_name[unique_ids[i]])
		#print(topMatchDict[unique_ids[i]])
		for key in topMatchDict[unique_ids[i]].keys():
			print(key)
			for val in topMatchDict[unique_ids[i]][key]:
				print(business_id_to_name[val])
		if numDone % 500 == 0:
			print("Mapped %.2f restaurants to top similar so far" % numDone)

		#topMatchMat[i] = ordered_indices[1:numToFind+1]
	#print topMatchMat
	topRestEnd = time.time()
	print("Mapping restaurants to top similar took: " + str(topRestEnd - topRestStart) + " seconds\n")
	return topMatchDict


# Generates a single json file containing the similarity matrix, unique ids list mapping sim matrix index to corresponding business id, and business id to name/business name to id dicts
def gen_data_file(minReviews=25, cutoff=5000, reduced_size=50, n_feats=5000, topNToFind=10):
	start = time.time()
	#minReviews = 25  # Change this to change minimum number of business reviews for it to be included in dataset
	#cutoff = 300 # Cut off at 300 businesses for size limitaitons, figure out later.
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
	unique_ids, reviews, ordered_business_categories = get_reviews_and_ids(cutoff, minReviews, business_name_to_id) # Also does filtering based on review count here
	get_reviews_end = time.time()
	print ("finished get_reviews_and_ids in " + str(get_reviews_end - get_reviews_start) + " seconds\n")
	#n_feats = 5000
	print("starting tfidf_vec.fit_transform()")
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
	# sim_mat_end = time.time()
	# print ("finished initial sim_mat generation in " + str(sim_mat_end - sim_mat_start) + " seconds\n")

	# perform SVD
	# svdStart = time.time()
	# print ("starting SVD")
	# #reduced_size = 50 # Can by changed as needed
	# lsa = TruncatedSVD(reduced_size, algorithm='randomized')
	# svd_matrix = lsa.fit_transform(restaurant_by_vocab_matrix)
	# svd_matrix = Normalizer(copy=False).fit_transform(svd_matrix) # copy=false to perform in place normalization, useful on larger dataset
	# sim_matrix = svd_matrix.dot(svd_matrix.T)
	# svdEnd = time.time()
	# print ("finished SVD in " + str(svdEnd - svdStart) + " seconds\n")
	# end SVD

	#topNToFind = 10 # Find top 10 most similar restaurants
	topMatchDict = map_restaurant_to_top_similar(restaurant_by_vocab_matrix, unique_ids, business_id_to_name, topNToFind)

	saveDataStart = time.time()

	data = {}
	data['business_id_to_name'] = business_id_to_name
	data['business_name_to_id'] = business_name_to_id
	data['topMatches'] = topMatchDict
	data['unique_ids'] = unique_ids
	data['ordered_business_categories'] = ordered_business_categories
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

	gen_data_file(minReviews=10, cutoff=50000, reduced_size=50, n_feats=5000, topNToFind=100)# Uncomment this to run preprocessing: Generates data file with sim matrix, business id/name dicts, and unique_ids for indexing business ids in sim matrix
	#mtx, unique_ids, business_id_to_name = load_precomputed_svds()
	#topNToFind = 10 # Find top 10 most similar restaurants
	#map_restaurant_to_top_similar(mtx, unique_ids, business_id_to_name, topNToFind)
