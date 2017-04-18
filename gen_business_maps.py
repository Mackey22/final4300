import json
from collections import defaultdict

def gen_business_id_to_name():
    """Return Dict - maps business id to business name."""
    business_id_to_name = defaultdict(str)
    with open('yelp_data/yelp_academic_dataset_business.json') as data_file:
        for line in data_file:
            data = (json.loads(line))
            business_id_to_name[data['business_id']] = data['name'].lower()
    with open('business_id_to_name.json', 'w') as fp:
    	json.dump(business_id_to_name, fp)


def gen_business_name_to_id():
    """Return Dict - maps business names to business ids."""
    business_name_to_id = defaultdict(str)
    with open('yelp_data/yelp_academic_dataset_business.json') as data_file:
        for line in data_file:
            data = (json.loads(line))
            business_name_to_id[data['name'].lower()] = data['business_id']
    with open('business_name_to_id.json', 'w') as fp:
    	json.dump(business_name_to_id, fp)

gen_business_id_to_name()