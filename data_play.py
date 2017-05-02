import json
from collections import defaultdict
from pprint import pprint
import numpy as np
import matplotlib.pyplot as plt

# 144072 businesses
# 4153150 reviews


def count_businesses():
    c = 0
    with open('yelp_data/yelp_academic_dataset_business.json') as data_file:
        for line in data_file:
            c += 1
    print str(c) + " businesses"


def count_reviews():
    c = 0
    with open('yelp_data/yelp_academic_dataset_review.json') as data_file:
        for line in data_file:
            c += 1
    print str(c) + " reviews"


def make_business_id_map():
    business_id_to_business = {}
    c = 0
    with open('yelp_data/yelp_academic_dataset_business.json') as data_file:
        for line in data_file:
            c += 1
            if c % 10000 == 0:
                print c
            data = json.loads(line)
            business_id_to_business[data["business_id"]] = {"data": data, "reviews": [], "review_count": 0}
    return business_id_to_business


def combine_reviews(business_id_map):
    c = 0
    with open('yelp_data/yelp_academic_dataset_review.json') as data_file:
        for line in data_file:
            c += 1
            if c % 10000 == 0:
                print c
            data = json.loads(line)

            business_id = data['business_id']
            text = data['text']

            business_id_map[business_id]["reviews"].append(text)
            business_id_map[business_id]["review_count"] += 1
    for v in business_id_map.values():
        v["reviews"] = " ".join(v["reviews"])
    pprint(business_id_map.values()[4])
    with open('out_data/try1.json', 'w') as fp:
        json.dump(business_id_map, fp, indent=4)


def read_json(filepath):
    return json.load(filepath)

# count_businesses()
# count_reviews()

# business_map = make_business_id_map()
# # pprint(business_map)
# combine_reviews(business_map)

with open("jsons/kardashian-transcripts.json") as df:
    data = json.load(df)["business_id_to_name"]

autocomplete_info = []

keys = data.keys()
for i in range(len(data)):
    key = keys[i]
    val = data[key]
    name = ", ".join([val[0], val[1], val[2]])
    d = {"name": name}
    autocomplete_info.append(d)

print len(autocomplete_info)

with open("autocomplete_info.json", "w") as df:
    json.dump(autocomplete_info, df)

# import json
# from collections import defaultdict
# from pprint import pprint
# import numpy as np
# import matplotlib.pyplot as plt


# reviewers = defaultdict(int)

# # Get counts of all these things
# count = 0
# with open('yelp_data/yelp_academic_dataset_review.json') as data_file:
#     for line in data_file:
#         count += 1
#         data = (json.loads(line))
#         if count == 5:
#             print data

#         reviewer = data['user_id']
#         reviewers[reviewer] += 1

# print count

# # Get the number of things with each of those counts

# # Plotting things


# def sort_dict_by_val(d):
#     """Get a list of a dict's keys ordered by descending values."""
#     return sorted(d, key=d.__getitem__, reverse=True)


# def make_hist(d, num_display, ylabel, xlabel, title):
#     sorted_keys = sort_dict_by_val(d)[:num_display]
#     sorted_vals = [d[k] for k in sorted_keys]

#     keys_tup = sorted_keys
#     vals_tup = sorted_vals

#     ind = np.arange(len(vals_tup))  # the x locations for the groups
#     width = 0.35       # the width of the bars

#     fig, ax = plt.subplots()
#     plt.bar(ind, vals_tup, width=width, color='r')

#     # add some text for labels, title and axes ticks
#     plt.ylabel(ylabel)
#     plt.xlabel(xlabel)
#     plt.title(title)
#     plt.xticks(ind + width / 2, keys_tup, rotation=23)

#     plt.savefig("graphs/" + title + ".png")
#     plt.clf()

# make_hist(reviewers, 10, "Number of Reviews", "User", "Top 10 Reviewers")
# # make_hist(cities, 10, "Number of Reviews", "City", "City Count")
# # make_hist(stars, 10, "Number of Reviews", "Rating", "Rating Frequency")
# # make_hist(review_count, 20, "Number of Restaurants with x Reviews", "Number of Reviews", "Review Frequency")
# # make_hist(categories, 10, "Number of Restaurants", "Category", "Top 10 Categories")

# # def do_some_analysis(g, show=False):
# #     values = sorted(centrality.values(), reverse=True)

# #     num_bins = 50

# #     fig, ax = plt.subplots()
# #     hist, bins = np.histogram(values, bins=num_bins)
# #     width = 0.7 * (bins[1] - bins[0])
# #     center = (bins[:-1] + bins[1:]) / 2
# #     plt.bar(center, hist, align='center', width=width)
# #     plt.ylabel("Number of Nodes")
# #     plt.xlabel("Closeness Centrality")
# #     plt.title("Centrality for alpha: " + str(a) + " and beta: " + str(b))

# #     plt.savefig("graphs/hist-" + str(k) + "_alpha-" + str(a) + "_beta-" + str(b) + ".png")
# #     if show:
# #         plt.show()
# #     plt.clf()



# # pprint(dict(cities))
# # pprint(dict(stars))
# # pprint(dict(types))
# # pprint(dict(review_count))
# # pprint(dict(categories))















# # Plotting things


# def sort_dict_by_val(d):
#     """Get a list of a dict's keys ordered by descending values."""
#     return sorted(d, key=d.__getitem__, reverse=True)


# def make_hist(d, num_display, ylabel, xlabel, title):
#     sorted_keys = sort_dict_by_val(d)[:num_display]
#     sorted_vals = [d[k] for k in sorted_keys]

#     keys_tup = sorted_keys
#     vals_tup = sorted_vals

#     ind = np.arange(len(vals_tup))  # the x locations for the groups
#     width = 0.35       # the width of the bars

#     fig, ax = plt.subplots()
#     plt.bar(ind, vals_tup, width=width, color='r')

#     # add some text for labels, title and axes ticks
#     plt.ylabel(ylabel)
#     plt.xlabel(xlabel)
#     plt.title(title)
#     plt.xticks(ind + width / 2, keys_tup, rotation=23)

#     plt.savefig("graphs/" + title + ".png")
#     plt.clf()


# make_hist(cities, 10, "Number of Reviews", "City", "City Count")
# make_hist(stars, 10, "Number of Reviews", "Rating", "Rating Frequency")
# make_hist(review_count, 20, "Number of Restaurants with x Reviews", "Number of Reviews", "Review Frequency")
# make_hist(categories, 10, "Number of Restaurants", "Category", "Top 10 Categories")

# # def do_some_analysis(g, show=False):
# #     values = sorted(centrality.values(), reverse=True)

# #     num_bins = 50

# #     fig, ax = plt.subplots()
# #     hist, bins = np.histogram(values, bins=num_bins)
# #     width = 0.7 * (bins[1] - bins[0])
# #     center = (bins[:-1] + bins[1:]) / 2
# #     plt.bar(center, hist, align='center', width=width)
# #     plt.ylabel("Number of Nodes")
# #     plt.xlabel("Closeness Centrality")
# #     plt.title("Centrality for alpha: " + str(a) + " and beta: " + str(b))

# #     plt.savefig("graphs/hist-" + str(k) + "_alpha-" + str(a) + "_beta-" + str(b) + ".png")
# #     if show:
# #         plt.show()
# #     plt.clf()



# # pprint(dict(cities))
# # pprint(dict(stars))
# # pprint(dict(types))
# # pprint(dict(review_count))
# # pprint(dict(categories))
