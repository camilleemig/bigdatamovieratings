from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from . import MostSimilarUsers

def index(request):

    return HttpResponse(MostSimilarUsers.find_predicted_ratings_for_user(1))