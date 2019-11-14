from django.shortcuts import render
from fuzzywuzzy import fuzz
from operator import itemgetter

# Create your views here.
from . DataSingleton import DataSingleton

def index(request):
    context = {}
    return render(request, 'ratings/index.html', context)

def movies(request):
    singleton = DataSingleton()
    all_movies_list = [(k,v) for v, k in singleton.indices_to_movies.items()]
    if 'q' in request.GET:
        match_tuple = []
        # get match
        for title, idx in all_movies_list:
            ratio = fuzz.ratio(title.lower(), request.GET['q'].lower())
            if ratio >= 30:
                match_tuple.append((title, idx, ratio))
        # sort
        match_tuple = sorted(match_tuple, key=itemgetter(2), reverse=True)
        all_movies_list = [(i[0], i[1]) for i in match_tuple]
        search_placeholder = request.GET['q']
        print(search_placeholder)
    else:
        all_movies_list = all_movies_list[:100]
        search_placeholder = None

    context = {
        'all_movies_list': all_movies_list,
        'search_placeholder': search_placeholder
    }
    return render(request, 'ratings/movies.html', context)

def movie(request, movie_id):
    singleton = DataSingleton()
    movie = singleton.indices_to_movies[int(movie_id)]
    context = {
        'movie': movie,
    }
    return render(request, 'ratings/movie.html', context)

def categories(request):
    singleton = DataSingleton()
    categories_list = list(singleton.genres)
    context = {
        'categories_list': categories_list,
    }
    return render(request, 'ratings/categories.html', context)

def category(request, category):
    singleton = DataSingleton()
    movies_set = set(singleton.genres[category])
    movies_list = [(k,v) for v, k in singleton.indices_to_movies.items() if k in movies_set][:100]
    movies_list = sorted([(k, v, singleton.movie_ratings[v]) for k, v in movies_list], key=itemgetter(2), reverse=True)
    movies_list = movies_list[:100]
    context = {
        'movies_list': movies_list,
        'category': category
    }
    return render(request, 'ratings/category.html', context)