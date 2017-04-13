import json
from collections import defaultdict
from pprint import pprint
import numpy as np
import matplotlib.pyplot as plt


cities = defaultdict(int)
stars = defaultdict(int)
review_count = defaultdict(int)
categories = defaultdict(int)

# Get counts of all these things
count = 0
with open('yelp_data/yelp_academic_dataset_business.json') as data_file:
    for line in data_file:
        count += 1
        data = (json.loads(line))

        city = data['city']
        star = data['stars']
        num_reviews = data['review_count']
        t = data['type']
        cats = data['categories']

        cities[city] += 1
        stars[star] += 1
        review_count[num_reviews] += 1
        if cats:
            for cat in cats:
                categories[cat] += 1

print count

# Get the number of things with each of those counts





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
