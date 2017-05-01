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


def string_cats(cats):
    res = ["Categories: "]
    for c in cats:
        res.append(c['title'])
        res.append(", ")
    return "".join(res[:-1])


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


def gen_table(output_list, contributing_words):
    """Return list of strings each formatted as html table."""
    s = []
    for i in range(len(output_list)):
        obj = output_list[i]
        s2_list = [
            "<div class='display_res'><div class='sub'>",
            string_words(contributing_words[i]),
            " stars</div><div class='sub'><img class='image-circle' src='",
            obj['image_url'],
            "' height=100 width=100></img></div><div class='sub'><h4><a href='",
            obj['url'],
            "'>",
            obj['name'],
            "</a></h4></div><div class='sub'>",
            str(obj['rating']),
            " stars</div><div class='sub'>",
            string_cats(obj['categories']),
            "</div><div class='sub'>",
            string_obj(obj['location']['display_address']),
            "</div></div><br> <br>"
        ]
        s2 = unidecode("".join(s2_list))

        s.append(format_html("{}", mark_safe(s2)))
    return s


def gen_category_list(output_list):
    """Return list of unique categories."""
    categories = set()
    for rest in output_list:
        cats = rest['categories']
        for c in cats:
            categories.add(c['title'])
    return sorted(list(categories))


def set_cats(obj):
    return set([c['title'] for c in obj['categories']])


def sort_by_category(output_list, chosen_categories, contributing_words):
    """Return restaurant list sorted by jaccard similarity of categories."""
    rest_scores = []
    for restaurant in output_list:
        cur_cats = set_cats(restaurant)
        all_cats = set(chosen_categories)
        score = len(cur_cats.intersection(all_cats)) / float(len(cur_cats.union(all_cats)))
        rest_scores.append((restaurant, score))

    rest_scores = sorted(rest_scores,key=lambda x:-x[1])
    # TODO: resort contributing words to match rest_scores
    return [res_score[0] for res_score in rest_scores], contributing_words

with open('autocomplete_info.json') as data_file:
                autocomplete_info = json.load(data_file)
autocomplete_info = json.dumps(autocomplete_info)


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

    # GET ALL INPUT VALUES
    if request.GET.get('search'):
        timing_gets = time.time()
        search = request.GET.get('search')
        # if request.GET.get('home'):
        # origin = request.GET.get('home')
        res = search.split(',')
        print res
        search = res[0].strip()
        origin_city = res[1].strip()
        origin_state = res[2].strip()
        print "Got params in", time.time() - timing_gets, "seconds"
        if request.GET.get('dest'):
            dest = request.GET.get('dest')
            output_list, best_match, contributing_words = find_similar(search, origin_city, dest)

            # IF CATEGORIES SELECTED, FILTER BY JACC SIM
            category_timer = time.time()
            if request.GET.get('categories'):
                chosen_categories = request.GET.getlist('categories')
                output_list, contributing_words = sort_by_category(output_list, chosen_categories, contributing_words)
                print "Category sorting took", time.time() - category_timer, "seconds"

            # CREATE TABLE OF RESULTS
            output_timer = time.time()
            output_html = gen_table(output_list, contributing_words)
            print "Generating output took", time.time() - output_timer, "seconds"
            paginate_timer = time.time()
            paginator = Paginator(output_html, 10)
            page = request.GET.get('page')
            try:
                    output = paginator.page(page)
            except PageNotAnInteger:
                    output = paginator.page(1)
            except EmptyPage:
                    output = paginator.page(paginator.num_pages)
            print "Paginating took", time.time() - paginate_timer, "seconds"

    if best_match == '':
        rest_loc = ''
    else:
        else_time = time.time()
        rest_loc = string.capwords(best_match) + ', ' + origin_city + ', ' + origin_state
        print "Else timer took", time.time() - else_time, "seconds"

    rendering_timer = time.time()
    rendered = render_to_response('project_template/index.html',
                            {'output': output,
                             'home_cities': home_cities,
                             "dest_cities": dest_cities,
                             'magic_url': request.get_full_path(),
                             # 'origin': origin,
                             'dest': dest,
                             'query': search,
                             'best_match': rest_loc,
                             'categories': gen_category_list(output_list),
                             'topics': ['topic 1','topice 2', 'topic 3', 'topic n'],
                             'auto_json': autocomplete_info
                             })
    print "Rendering took", time.time() - rendering_timer, "seconds"
    print "Total time was", time.time() - start_time, "seconds"
    return rendered
