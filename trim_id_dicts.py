import json

with open("jsons/kardashian-transcripts.json") as fp:
    data = json.load(fp)


unique_ids = data['unique_ids']
print len(unique_ids)
business_id_to_name = data['business_id_to_name']
business_name_to_id = data['business_name_to_id']

new_business_id_to_name = {}
new_business_name_to_id = {}

for i in range(5):
    idkeys = business_id_to_name.keys()
    print idkeys[i], business_id_to_name[idkeys[i]]

    namekeys = business_name_to_id.keys()
    print namekeys[i], business_name_to_id[namekeys[i]]

for uid in unique_ids:
    new_business_id_to_name[uid] = business_id_to_name[uid]

    name = business_id_to_name[uid][0]

    if name not in new_business_name_to_id:
        id_array = []
        town_array = []
        state_array = []
        address_array = []
        for i, identifier in enumerate(business_name_to_id[name][0]):
            if identifier in unique_ids:
                id_array.append(identifier)
                town_array.append(business_name_to_id[name][1][i])
                state_array.append(business_name_to_id[name][2][i])
                address_array.append(business_name_to_id[name][3][i])
        new_business_name_to_id[name] = [id_array, town_array, state_array, address_array]

data['business_id_to_name'] = new_business_id_to_name
data['business_name_to_id'] = new_business_name_to_id

with open("jsons/kardashian-transcripts.json", "w") as fp:
    json.dump(data, fp)
