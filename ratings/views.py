from django.shortcuts import render
# Create your views here.
from . import MostSimilarUsers

def index(request):
    all_movies_list = MostSimilarUsers.find_predicted_ratings_for_user(1)
    context = {
        'all_movies_list': all_movies_list,
    }
    return render(request, 'ratings/index.html', context)