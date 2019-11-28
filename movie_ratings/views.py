from django.shortcuts import render
from fuzzywuzzy import fuzz
from operator import itemgetter
from .models import Rating

# Create your views here.
from . DataSingleton import DataSingleton
from . MostSimilarUsers import find_predicted_ratings_for_data
from . MostSimilarMovies import KnnRecommender
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    singleton = DataSingleton()
    rated = Rating.objects.filter(user=request.user)
    data = dict([(singleton.indices_to_movies[r.movie], r.rating) for r in rated if r.rating])
    if data:
        predictions = find_predicted_ratings_for_data(data)[:10]
        for i, pred in enumerate(predictions):
            predictions[i] = list(pred) + [singleton.reverse[pred[0]], i % 3 == 0]
    else:
        predictions = []
    context = {"predictions": predictions, 'rated': rated}

    return render(request, 'movie_ratings/index.html', context)

@login_required
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
    return render(request, 'movie_ratings/movies.html', context)

@login_required
def movie(request, movie_id):
    singleton = DataSingleton()
    movie = [movie_id, singleton.indices_to_movies[int(movie_id)]]

    try:
        movie_rating = Rating.objects.get(user=request.user, movie=movie_id)
    except (KeyError, Rating.DoesNotExist):
        movie_rating = Rating(user=request.user, movie=movie_id)
        movie_rating.save()
    rec = KnnRecommender()
    most_similar = list(rec.make_recommendations(movie[1], 5))
    for i, pred in enumerate(most_similar):
        most_similar[i] = [pred, None, singleton.reverse[pred], i % 3 == 0]
    context = {
        'movie': movie,
        'movie_rating': movie_rating,
        'predictions': most_similar
    }
    return render(request, 'movie_ratings/movie.html', context)

@login_required
def categories(request):
    singleton = DataSingleton()
    categories_list = list(singleton.genres)
    context = {
        'categories_list': categories_list,
    }
    return render(request, 'movie_ratings/categories.html', context)

@login_required
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
    return render(request, 'movie_ratings/category.html', context)

@login_required
def rate(request, movie_id):
    singleton = DataSingleton()
    movie = [movie_id, singleton.indices_to_movies[int(movie_id)]]
    try:
        movie_rating = Rating.objects.get(user=request.user, movie=movie_id)
    except (KeyError, Rating.DoesNotExist):
        movie_rating = Rating(user=request.user, movie=movie_id)
    movie_rating.rating = request.POST['choice']
    movie_rating.save()
    rec = KnnRecommender()
    most_similar = list(rec.make_recommendations(movie[1], 5))
    for i, pred in enumerate(most_similar):
        most_similar[i] = [pred, None, singleton.reverse[pred], i % 3 == 0]
    context = {
        'movie': movie,
        'movie_rating': movie_rating,
        'predictions': most_similar
    }
    return render(request, 'movie_ratings/movie.html', context)