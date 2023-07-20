from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Genre, Movie
from .serializers import GenreSerializer, MovieSerializer


#Note to self, create a late fee charge custom view in the Order view 
#  to calculate the fees to be paid when a movie is returned late.

# Create your views here.

#function to create a rest_framework view which handles requests 
# and gives objects as its response, depending on the methods specified.
@api_view(['GET', 'POST'])
def movie_list(request):
    if request.method == 'GET':
        #eagerloading the movies with their genres to speed up queries.
        queryset = Movie.objects.prefetch_related('genres').all()
        #Returning all movies by iterating on it using the many keyword.
        serializer = MovieSerializer(queryset, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        #Deserislizing the JSON data object passed by the client into a python object
        serializer = MovieSerializer(data=request.data)
        #Validating the data in order to save it
        serializer.is_valid()
        #Returning the validated data
        return Response(serializer.validated_data)

@api_view()
def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    #Converting the movie gotten with its id to a dictionary.
    serializer = MovieSerializer(movie)
    #Getting and returning the ditionary data in JSON format.
    return Response(serializer.data)


@api_view()
def genre_list(request):
    queryset = Genre.objects.prefetch_related('movie').all()
    serializer = GenreSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view()
def genre_detail(request, pk):
    genre = get_object_or_404(Genre, pk=pk)
    serializer = GenreSerializer(genre)
    return Response(serializer.data)
    
