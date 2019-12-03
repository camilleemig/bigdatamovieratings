from django.shortcuts import render
from fuzzywuzzy import fuzz
from operator import itemgetter
from .models import Rating

# Create your views here.
from . MovieRatingData import MovieRatingData
from . MostSimilarUsers import find_predicted_ratings_for_data, find_predicted_ratings_for_similar_movies
from . MostSimilarMovies import KnnRecommender
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    singleton = MovieRatingData()
    rated = Rating.objects.filter(user=request.user)
    data = dict([(singleton.movieId_to_movieName[r.movie], r.rating) for r in rated if r.rating])
    if data:
        predictions = find_predicted_ratings_for_data(data)[:10]
        for i, pred in enumerate(predictions):
            predictions[i] = list(pred) + [singleton.movieName_to_movieId[pred[0]], i % 5 == 0]
        similar_movies = find_predicted_ratings_for_similar_movies(data)[:10]
        for i, pred in enumerate(similar_movies):
            similar_movies[i] = list(pred) + [singleton.movieName_to_movieId[pred[0]], i % 5 == 0]
    else:
        predictions = []
        similar_movies = []
    ratings = [[singleton.movieId_to_movieName[r.movie], r.rating, r.movie] for r in rated if r.rating]
    for i, rating in enumerate(ratings):
        ratings[i] = rating + [i % 5 == 0]
    context = {"predictions": predictions, 'ratings': ratings, 'similar_movies': similar_movies}

    return render(request, 'movie_ratings/index.html', context)

@login_required
def movies(request):
    singleton = MovieRatingData()
    all_movies_list = [(k,v) for v, k in singleton.movieId_to_movieName.items()]
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
        context = {
            'all_movies_list': all_movies_list,
            'search_placeholder': search_placeholder
        }
    else:
        movies_dict = {c: [(m, singleton.average_movie_ratings[m]) for m in k] for c, k in singleton.genres.items()}
        movies_dict = {c: sorted(v, key=itemgetter(1), reverse=True)[:5] for c, v in movies_dict.items()}
        movies_dict = {c: [(m[0], singleton.movieId_to_movieName[m[0]]) for m in v] for c, v in movies_dict.items()}

        context = {
            'movies_dict': movies_dict
        }
    return render(request, 'movie_ratings/movies.html', context)

@login_required
def movie(request, movie_id):
    singleton = MovieRatingData()
    movie = [movie_id, singleton.movieId_to_movieName[int(movie_id)]]

    try:
        movie_rating = Rating.objects.get(user=request.user, movie=movie_id)
    except (KeyError, Rating.DoesNotExist):
        movie_rating = Rating(user=request.user, movie=movie_id)
        movie_rating.save()
    rec = KnnRecommender()
    most_similar = list(rec.make_recommendations(movie[1]))
    for i, pred in enumerate(most_similar):
        most_similar[i] = [pred, None, singleton.movieName_to_movieId[pred], i % 5 == 0]
    context = {
        'movie': movie,
        'movie_rating': movie_rating,
        'predictions': most_similar
    }
    return render(request, 'movie_ratings/movie.html', context)

@login_required
def categories(request):
    singleton = MovieRatingData()
    categories_list = list(singleton.genres)
    context = {
        'categories_list': categories_list,
    }
    return render(request, 'movie_ratings/categories.html', context)

@login_required
def category(request, category):
    singleton = MovieRatingData()
    movies_set = set(singleton.genres[category])
    movies_list = [(singleton.movieId_to_movieName[k], k) for k in movies_set][:100]
    movies_list = sorted([(k, v, singleton.average_movie_ratings[v]) for k, v in movies_list], key=itemgetter(2), reverse=True)
    movies_list = movies_list[:100]
    context = {
        'movies_list': movies_list,
        'category': category
    }
    return render(request, 'movie_ratings/category.html', context)

@login_required
def rate(request, movie_id):
    singleton = MovieRatingData()
    movie = [movie_id, singleton.movieId_to_movieName[int(movie_id)]]
    try:
        movie_rating = Rating.objects.get(user=request.user, movie=movie_id)
    except (KeyError, Rating.DoesNotExist):
        movie_rating = Rating(user=request.user, movie=movie_id)
    movie_rating.rating = request.POST['choice']
    movie_rating.save()
    rec = KnnRecommender()
    most_similar = list(rec.make_recommendations(movie[1]))
    for i, pred in enumerate(most_similar):
        most_similar[i] = [pred, None, singleton.movieName_to_movieId[pred], i % 5 == 0]
    context = {
        'movie': movie,
        'movie_rating': movie_rating,
        'predictions': most_similar
    }
    return render(request, 'movie_ratings/movie.html', context)