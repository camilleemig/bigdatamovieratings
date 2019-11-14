from django.shortcuts import render
# Create your views here.
from . DataSingleton import DataSingleton

def index(request):
    singleton = DataSingleton()
    all_movies_list = [(k,v+1) for k, v in singleton.movies_to_indices.items()]
    context = {
        'all_movies_list': all_movies_list,
    }
    return render(request, 'ratings/index.html', context)

def movie(request, movie_id):
    singleton = DataSingleton()
    movie = singleton.indices_to_movies[int(movie_id)]
    context = {
        'movie': movie,
    }
    return render(request, 'ratings/movie.html', context)