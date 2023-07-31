from django.shortcuts import get_object_or_404
from django.db.models.aggregates import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .filters import GenreFilters, MovieFilters, CartItemFilters
from .models import Cart, CartItem, Customer,Genre, Movie, Review
from .serializers import AddCartItemSerializer, CartSerializer, CartItemSerializer, CustomerSerializer, GenreSerializer, MovieSerializer, ReviewSerializer, UpdateCartItemSerializer


#Note to self, create a late fee charge custom view in the Order view 
#  to calculate the fees to be paid when a movie is returned late.

# Create your views here.

#Class to create a rest_framework view which handles requests 
# and gives objects as its response, depending on the methods specified.

class MovieViewSet(ModelViewSet):
    queryset = Movie.objects.prefetch_related('genres').all()
    serializer_class = MovieSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MovieFilters
    search_fields = ['title', 'genres__title']
    ordering_fields = ['daily_rental_rate', 'last_update']

    

    
    def get_serializer_context(self):
        return {'request': self.request}

    #Overriding the Destroy mixin in the ApiView since there is additional logic here.
    def delete(self, request, pk):
        movie = get_object_or_404(Movie, pk=pk)
        if movie.rentorderitems.count() > 0:
            return Response({'error': 'Movie cannot be deleted because it is associated with a rent orderitem'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
 
        



class GenreViewSet(ModelViewSet):
    queryset = Genre.objects.annotate(movie_count=Count('movie')).all().prefetch_related('movie')

    serializer_class = GenreSerializer
  
    filter_backends = [DjangoFilterBackend]
    #Specifying the class to be used to filter
    filterset_class = GenreFilters
    

    def delete(self, request, pk):
        #Getting a single genre using the pk
        genre = get_object_or_404(Genre, pk=pk)
        if genre.movie.count() > 0:
            return Response({'error': 'Genre Cannot be deleted as it still is referencing a movie'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        genre.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_serializer_context(self):
        return {'movie_id': self.kwargs.get('movie_pk')}



class CartViewSet(mixins.CreateModelMixin, 
                  mixins.RetrieveModelMixin, 
                  mixins.UpdateModelMixin, 
                  mixins.DestroyModelMixin, 
                  GenericViewSet):
    #Performing an eager load where we get all items related with cart and also the related movies of each item.
    queryset = Cart.objects.prefetch_related('items__movie').all()
    serializer_class = CartSerializer
        



class CartItemViewSet(ModelViewSet):
    #List of http method names that we allow
    http_method_names = ['get', 'post', 'patch', 'delete']


    filter_backends = [DjangoFilterBackend]
    filterset_class = CartItemFilters

    #Since we don't want to return all cart items and only want to return items based
    #on the cart id given, we would have to override the queryset.
    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('movie')
    
    #function to return a serializer class depending on the operation the user seeks to carry out
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    #function to extract the cart id from the urls defined in urls.py
    def get_serializer_context(self):
        return {'cart_id': self.kwargs.get('cart_pk')}
            


class ReviewViewset(ModelViewSet):
    serializer_class = ReviewSerializer

    #overidding the queryset method in order to filter based on the movie id provided 
    #in the query parameters. SO if url is hub/movies/2/reviews/, we would only look at
    #the reviews for the movies with id, 2.
    def get_queryset(self):
        return Review.objects.filter(movie_id=self.kwargs['movie_pk'])
    

    #Function to gain access to the information passed in to the fields in self.kwargs
    #  by the user for serialiazition
    # and passing it to the serializer module.
    def get_serializer_context(self):
        return {'movie_id': self.kwargs.get('movie_pk')}


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    #Function to get the current customer's profile. This would be an action
    #  that is why it is defined with an action decorator. Detail is set to False to allow
    # it to be included in the customer list view else it would be available on the
    # customer detail view.

    @action(detail=False)
    def me(self, request):
        #Getting information about the current logged in user from the authenticated middleware
        #We are using a tuple because it would give us both the value for the current  
        #logged in user and a boolean status result. if it does not exist it would return as an anonymous user.
        # The get_or_create method is incase we do not have a current logged in user when trying to update data. 
        (customer, created) = Customer.objects.get_or_create(user_id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'POST':
            #Passing in the current customer logged in and the data to be updated
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

