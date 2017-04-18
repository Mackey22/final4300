import json

from collections import defaultdict
from helpers import sort_dict_by_val


def get_ordered_cities():
    cities = defaultdict(int)
    with open('../yelp_data/yelp_academic_dataset_business.json') as data_file:
        for line in data_file:
            data = json.loads(line)
            cities[data['city']] += 1
    dests = sort_dict_by_val(cities)

    with open('../jsons/ordered_cities.json', 'w') as fp:
        json.dump(dests, fp, indent=4)

if __name__ == "__main__":
    get_ordered_cities()
    print "ordered cities"
