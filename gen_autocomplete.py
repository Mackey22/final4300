import json
import string

with open('business_id_to_name.json') as data_file:
        business_id_to_name = json.load(data_file)

auto_info = []
for _ , info in business_id_to_name.iteritems():
	# data = {"name": string.capwords(info[0]), "state": info[2].upper(), "city": string.capwords(info[1])}
	data = {"name": string.capwords(info[0]) + ", " + string.capwords(info[1]) + ", " + info[2].upper() }
	auto_info.append(data)

with open('autocomplete_info.json', 'w') as fp:
        json.dump(auto_info, fp)

with open('autocomplete_info.json') as data_file:
        autocomplete_info = json.load(data_file)
print autocomplete_info[0]
autocomplete_info = json.dumps(autocomplete_info)






