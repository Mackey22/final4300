# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from .models import Docs
from django.template import loader
from .form import QueryForm
from .test import find_similar, get_ordered_cities
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.html import format_html, mark_safe
import json
import string
import time
from unidecode import unidecode
# #url for reviews: # https://api.yelp.com/v3/businesses/{id}/reviews


def string_obj(obj):
    res = ["Location:"]
    for c in obj:
        res.append(c)
    return " ".join(res)


def string_words(l):
    res = []
    for w in l:
        res.append(str(w))
    return " ".join(res)


def gen_table(output_list):
    print ("length output_list")
    print (len(output_list))
    """Return list of strings each formatted as html table"""
    s = []
    for i in range(len(output_list)):
        try:
            s2 ="<div> hELLO </div>"
            # obj = output_list[i]
            # print "object", obj
            # s2 = "<div class='display_res'>"
            # s2 += "<div class='sub'><img class='image-circle' src='" + obj['image_url'] + "' height=100 width=100></img>" + "</div>"
            # s2 += "<div class='sub'><h4><a href='" + obj['url'] + "'>" + obj['name'] + "</a></h4></div>"
            # s2 += "<div class='sub'>" + "Price: " + obj['price'] + "</div>"
            # s2 += "<div class='sub'>" + "Review count: " + str(obj['review_count']) + "</div>"
            # s2 += "<div class='sub'>" + " Similar aspects: " + string_words(obj['categories']) + "</div>"
            # s2 += "<div class='sub'>" + str(obj['rating']) + " stars</div>"
            # s2 += "<div class='sub'>" + string_obj(obj['location']['display_address']) + "</div>"
            # s2 += "<div class='sub'>" + "Phone: " + obj['display_phone'] + "</div>"
            # s2 += "</div><br> <br>"
            # s2 = unidecode(s2)
            s.append(format_html("{}", mark_safe(s2)))
        except:
            pass


def gen_category_list(output_list):
    """Return list of unique categories."""
    categories = set()
    for rest in output_list:
        cats = rest['categories']
        for c in cats:
            categories.add(c)
    return sorted(list(categories))


def sort_by_category(output_list, chosen_categories):
    """Return restaurant list sorted by jaccard similarity of categories."""
    rest_scores = []
    for restaurant in output_list:
        cur_cats = set(restaurant["categories"])
        all_cats = set(chosen_categories)
        score = len(cur_cats.intersection(all_cats)) / float(len(cur_cats.union(all_cats)))
        rest_scores.append((restaurant, score))

    rest_scores = sorted(rest_scores,key=lambda x:-x[1])
    # TODO: resort contributing words to match rest_scores
    return [res_score[0] for res_score in rest_scores]


def list_cats(restObj):
    cats = []
    if restObj != []:
        for cat in restObj['categories']:
            cats.append(cat['title'])
    return cats


def remake_output(output_list, contributing_words):
    for i in range(len(output_list)):
        restObj = output_list[i]
        cats = list_cats(restObj)
        print "cats", cats
        print "topics", contributing_words[i]
        for word in contributing_words[i]:
            cats.append(word)
        restObj['categories'] = list(set(cats))
    print (output_list)

    for x in output_list:
        print x['categories']
    return output_list


def index(request):
    """Create views here."""
    start_time = time.time()
    output_list = ''
    output = ''

    dest_cities, home_cities = get_ordered_cities()
    origin_city = ''
    origin_state = ''
    dest = 'Please select a destination'
    search = ''
    best_match = ''
    display_topics_categories = []

    with open('autocomplete_info.json') as data_file:
        autocomplete_info = json.load(data_file)
    autocomplete_info = json.dumps(autocomplete_info)

    # GET ALL INPUT VALUES
    if request.GET.get('search'):
        search = request.GET.get('search')
        # if request.GET.get('home'):
        # origin = request.GET.get('home')
        res = search.split(',')
        print res
        search = res[0].strip()
        origin_city = res[1].strip()
        origin_state = res[2].strip()
        if request.GET.get('dest'):
            dest = request.GET.get('dest')
            output_list, best_match, contributing_words, _ = find_similar(search, origin_city, dest)

            # initialize all topics and categories
            print ('before')
            print ('after')

            output_list = remake_output(output_list, contributing_words)
            display_topics_categories = gen_category_list(output_list)
            print ("output is")
            print (output_list)

            # IF CATEGORIES SELECTED, FILTER BY JACC SIM
            if request.GET.get('categories'):
                chosen_categories_and_topics = request.GET.getlist('categories')
                output_list = sort_by_category(output_list, chosen_categories_and_topics)
                print ("output modified:")
                print (output_list)

            # CREATE TABLE OF RESULTS
            output_html = gen_table(output_list)
            paginator = Paginator(output_html, 10)
            page = request.GET.get('page')
            try:
                output = paginator.page(page)
            except PageNotAnInteger:
                output = paginator.page(1)
            except EmptyPage:
                output = paginator.page(paginator.num_pages)
    if best_match == '':
        rest_loc = ''
    else:
        rest_loc = string.capwords(best_match) + ', ' + origin_city + ', ' + origin_state
    print "Total time was", time.time() - start_time, "seconds"
    return render_to_response('project_template/index.html',
                        {'output': output,
                         "dest_cities": dest_cities,
                         'magic_url': request.get_full_path(),
                         # 'origin': origin,
                         'dest': dest,
                         'query': search,
                         'best_match': rest_loc,
                         'categories': display_topics_categories,
                         'auto_json': autocomplete_info
                         })
