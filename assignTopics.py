import json
import numpy as np
from topic_modeling import get_similar_topics

with open('jsons/kardashian-transcripts.json') as fp:
    data = json.load(fp)
    business_id_to_name = data['business_id_to_name']
    business_name_to_id = data['business_name_to_id']
    topMatchDict = data['topMatches']
    unique_ids = data['unique_ids']
    ordered_business_categories = data['ordered_business_categories']
    cities = data['cities']
    # contributingWordsDict = data['contributing_words']

with open('doc_topic_mtx.json') as fp:
    doc_topic_mtx = json.load(fp)

with open('topicid_to_label.json') as fp:
    topicid_to_label = json.load(fp)

contributingWordsDict = {}

for idx, unique_id in enumerate(unique_ids):
    queryDicts = topMatchDict[unique_id]
    contributingWordsDict[unique_id] = {}
    for city, matchList in queryDicts.iteritems():
        for matchId in matchList:
            matchIdx = unique_ids.index(matchId)
            contributingWordsDict[unique_id][matchId] = get_similar_topics(idx, matchIdx, topicid_to_label, doc_topic_mtx)

data = {}
data['business_id_to_name'] = business_id_to_name
data['business_name_to_id'] = business_name_to_id
data['topMatches'] = topMatchDict
data['unique_ids'] = unique_ids
data['ordered_business_categories'] = ordered_business_categories
data['cities'] = cities
data['contributing_words'] = contributingWordsDict

with open('jsons/kardashian-transcripts.json', 'w') as fp:
    json.dump(data, fp)
