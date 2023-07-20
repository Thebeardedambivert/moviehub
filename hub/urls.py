from django.urls import path
from . import views

urlpatterns = [
    path('movies/', views.movie_list),
    path('movies/<int:pk>/', views.movie_detail),
    path('genres/', views.genre_list),
    path('genres/<int:pk>/', views.genre_detail),
]
