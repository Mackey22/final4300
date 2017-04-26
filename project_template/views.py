from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from .models import Docs
from django.template import loader
from .form import QueryForm
from .test import find_similar, get_ordered_cities
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.html import format_html, mark_safe

# {  
#    u'rating':4.0,
#    u'review_count':113,
#    u'name':u'Adega Restaurante',
#    u'transactions':[  

#    ],
#    u'url':   u'https://www.yelp.com/biz/adega-restaurante-toronto?adjust_creative=xGJw03IyUyyPy4XuNn4h_A&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=xGJw03IyUyyPy4XuNn4h_A',
#    u'price':u'$$$',
#    u'distance':2180.804403016,
#    u'coordinates':{  
#       u'latitude':43.65732,
#       u'longitude':-79.38323
#    },
#    u'phone':u'+14169774338',
#    u'image_url':   u'https://s3-media4.fl.yelpcdn.com/bphoto/UzurNBYVRhkPbozIePS-SQ/o.jpg',
#    u'categories':[  
#       {  
#          u'alias':u'portuguese',
#          u'title':u'Portuguese'
#       },
#       {  
#          u'alias':u'spanish',
#          u'title':u'Spanish'
#       }
#    ],
#    u'display_phone':u'+1 416-977-4338',
#    u'id':u'adega-restaurante-toronto',
#    u'is_closed':False,
#    u'location':{  
#       u'city':u'Toronto',
#       u'display_address':[  
#          u'33 Elm St',
#          u'Toronto,
#          ON M5G 1H1',
#          u'Canada'
#       ],
#       u'country':u'CA',
#       u'address2':u'',
#       u'address3':u'',
#       u'state':u'ON',
#       u'address1':u'33 Elm St',
#       u'zip_code':u'M5G 1H1'
#    }
# }

def string_cats(cats):
  res = "Categories: "
  for c in cats:
    res += c['title']+", "
  return res

def string_obj(obj):
  res = "Location: "
  for c in obj:
    res += c + " "
  return res

def gen_table(output_list):

  s = []
  for obj in output_list:
    s2 = "<table width=90%"
    s2 += "<tr><td><img src='" + obj['image_url']  + "' height=100 width=100></img>" + "</td>"
    s2 += "<td><a href='" + obj['url'] + "'>" + obj['name'] + "</a></td></tr>"
    s2 += "<tr><td>" + str(obj['rating']) + " stars</td></tr>"
    s2 += "<tr><td>" + string_cats(obj['categories']) + "</td></tr>"
    s2 += "<tr><td>" + string_obj(obj['location']['display_address']) + "</td></tr>"
    s2 += "</table><br><br>"
    s.append(format_html("{}", mark_safe(s2)))

  return s

# https://api.yelp.com/v3/businesses/{id}/reviews


def index(request):
    """Create views here."""
    output_list = ''
    output = ''
    dest_cities, home_cities = get_ordered_cities()
    origin = ''
    dest = ''
    search = ''
    best_match = ''
    if request.GET.get('search'):
        search = request.GET.get('search')
        if request.GET.get('home'):
          origin = request.GET.get('home')
          if request.GET.get('dest'):
            dest = request.GET.get('dest')
            output_list, best_match = find_similar(search, origin, dest)
            #create table of results
            output_html = gen_table(output_list)
            output_list = output_html
            paginator = Paginator(output_list, 10)
            page = request.GET.get('page')
            try:
                output = paginator.page(page)
            except PageNotAnInteger:
                output = paginator.page(1)
            except EmptyPage:
                output = paginator.page(paginator.num_pages)
    return render_to_response('project_template/index.html',
                          {'output': output,
                           'home_cities': home_cities,
                           "dest_cities": dest_cities,
                           'magic_url': request.get_full_path(),
                           'origin': ["Origin City: " + origin],
                           'dest': ["Destination City: " + dest],
                           'query': ["You searched: " + search],
                           'best_match': ["Best match was: " + best_match]
                           })
