from django.shortcuts import render
# Create your views here.
from . DataSingleton import DataSingleton

def index(request):
    context = {}
    return render(request, 'ratings/index.html', context)

def movies(request):
    singleton = DataSingleton()
    all_movies_list = [(k,v) for v, k in singleton.indices_to_movies.items()][:100]
    context = {
        'all_movies_list': all_movies_list,
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

    context = {
        'movies_list': movies_list,
        'category': category
    }
    return render(request, 'ratings/category.html', context)