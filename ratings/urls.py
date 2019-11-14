from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('movies/', views.movies, name='movies'),
    path('categories/', views.categories, name='categories'),
    path('<int:movie_id>/', views.movie, name='movie'),
    path('<str:category>/', views.category, name='category'),
]