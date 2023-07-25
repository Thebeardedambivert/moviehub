import django_filters
from .models import Movie, Genre


#Custom class for filtering where we specify the traverse the relationship paths of a many to many relationship
# using a double underscore. 
class GenreFilters(django_filters.FilterSet):
    movie_id = django_filters.CharFilter( field_name='movie__id', lookup_expr='exact')

    class Meta:
        model = Genre
        fields = ['movie']


class MovieFilters(django_filters.FilterSet):
    genres_id = django_filters.CharFilter(field_name='genres__id', lookup_expr='exact')

    class Meta:
        model = Movie
        fields = {'genres': ['exact'], 
                  'daily_rental_rate': ['gt', 'lt'],
                  'inventory': ['gt', 'lt']
                  }