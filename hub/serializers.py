#Model to convert python objects to dictionaries so that we can pass it to the views to handle requests 
#and convert these dictionaries to JSON.

from decimal import Decimal
from django.db.models.aggregates import Count
from django_filters.rest_framework import DjangoFilterBackend
from .models import Genre, Movie, Review 
from rest_framework import serializers


#class to convert the list of genres into dictionary objects
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'title', 'movie', 'movie_count']
        #Using the read only attribute makes it possible for the reverse relationship not
        # to run into an error when trying to write to the field which was annotated.
    movie_count = serializers.IntegerField(read_only=True)
    
    # def movie_id(self):
    #     movie_id = self.context.get('movie_id')
    #     return movie_id
    movie = serializers.StringRelatedField(many=True)
    

    
    

    #I may need to change how we pass information to the movie serializer by
    # updating the field using a ListField instead. I should attempt to achieve this when I 
    # have learned how to dynamically extract the queryset from a view using a serializer context instead of just 
    # querying all the movies one by one which is going to affect the performance of the code.
    #movie = serializers.ListField(child=serializers.PrimaryKeyRelatedField(queryset=Genre.objects.filter(movie__id=movie_id), many=True), allow_empty=False)
 
     

    

    
    # movies = serializers.SerializerMethodField(method_name='get_movies')

    # def get_movies(self, obj):
    #     return ", ".join([movie.title for movie in obj.movie_genres.all()])


    



#Class to convert the list of movies to dictionary objects
class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'daily_rental_rate', 'inventory','age_rating', 'price_with_tax', 'genres']

    
    #genres = serializers.SerializerMethodField(method_name='get_genres_title')
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    genres = GenreSerializer(many=True)

    #Providing a string representation of the related genres field, rendering each genre in a 
    #string format.
    def get_genres_title(self, obj):
        return ", ".join([genre.title for genre in obj.genres.all()])
    
    def get_genres_id(self, obj):
        return ", ".join([genre.id for genre in obj.genres.all()])

    #Serializer method to calulate tax. We include this in the fields list because django looks 
    # at the fields in the serializer class before looking at the fields in the models.
    def calculate_tax(self, movie: Movie):
        return movie.daily_rental_rate * Decimal(1.1)
    


#Serializer class to convert the list of reviews to dictionary objects
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description', 'movie']

    #overriding create method to include the movie id in the validated data dictionary
    #This allows the movie id to be included inherently in the validated data without having
    # to add it as one of the fields.
    def create(self, validated_data):
        movie_id = self.context['movie_id']
        return Review.objects.create(movie_id=movie_id, **validated_data)