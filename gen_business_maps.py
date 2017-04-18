import json
from collections import defaultdict

cutoff = 100 # This has to match the cutoff used in similarity.py. Maybe even just move these functions to that file

def gen_business_id_to_name(cutoff):
    """Return Dict - maps business id to business name."""
    business_id_to_name = defaultdict(str)
    with open('yelp data/yelp_academic_dataset_business.json') as data_file:
        count = 0
        for line in data_file:
            count += 1
            data = (json.loads(line))
            business_id_to_name[data['business_id']] = (data['name'].lower(), data['city'].lower(), data['state'].lower())
            if count > cutoff:
                break
    with open('business_id_to_name.json', 'w') as fp:
    	json.dump(business_id_to_name, fp)


def gen_business_name_to_id(cutoff):
    """Return Dict - maps business names to business ids."""
    business_name_to_id = defaultdict(str)
    with open('yelp data/yelp_academic_dataset_business.json') as data_file:
        count = 0
        for line in data_file:
            count += 1
            data = (json.loads(line))
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

gen_business_id_to_name(cutoff)
gen_business_name_to_id(cutoff)