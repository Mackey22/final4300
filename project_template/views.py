from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from .models import Docs
from django.template import loader
from .form import QueryForm
from .test import find_similar, get_ordered_cities
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


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
