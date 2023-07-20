#Modele to convert python objects to dictionaries so that we can pass it to the views to handle requests 
#and convert these dictionaries to JSON.

from decimal import Decimal
from .models import Genre, Movie 
from rest_framework import serializers


#class to convert the list of genres into dictionary objects
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'title']

    



#Class to convert the list of movies to dictionary objects
class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'daily_rental_rate', 'age_rating', 'price_with_tax', 'genres']

    
    #genres = serializers.SerializerMethodField(method_name='get_genres')
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    genres = GenreSerializer(many=True)

    #Providing a string representation of the related genres field, rendering each genre in a 
    #string format.
    def get_genres(self, obj):
        return ", ".join([genre.title for genre in obj.genres.all()])

    #Serializer method to calulate tax. We include this in the fields list because django looks 
    # at the fields in the serializer class before looking at the fields in the models.
    def calculate_tax(self, movie: Movie):
        return movie.daily_rental_rate * Decimal(1.1)