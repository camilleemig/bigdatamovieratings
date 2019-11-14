from django.shortcuts import render
# Create your views here.
from . DataSingleton import DataSingleton

def index(request):
    singleton = DataSingleton()
    all_movies_list = singleton.all_movies
    context = {
        'all_movies_list': all_movies_list,
    }
    return render(request, 'ratings/index.html', context)