from django.forms import DecimalField
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.generics import ListCreateAPIView

from hub.models import Customer, Genre, Movie, RentOrder

# Create your views here.
#Views are request handlers, imagine them as pipes that the request and responses from the 
# frontend client passes through
# to the server. A response is shaped depending on how the view is defined.

def say_hello(request):
    return render(request, 'hello.html', {'name': 'Uzo'})


#function to load movies with their promotions and genres
def movie_with_promotions(request):
    queryset = Movie.objects.prefetch_related('promotions').prefetch_related('genres')


#function to query movies with their genres
def movie_with_genres(request):
    queryset = Movie.objects.prefetch_related('moviegenres__genre_id').filter()


def genres_with_movies(request):
    queryset = Genre.objects.prefetch_related('moviegenres__movie_id')


#Function to query orders and their items with the movies this items belong to.

def orders_and_items(request):
    queryset = RentOrder.objects.prefetch_related('rentorderitems_set__movie')


# This should be in the view where there is an option for us to fill in 
# daily_rental_rate and n days.

def customercharge(daily_rental_rate, n_days):
    charge = [daily_rental_rate * days for days in n_days]
    return charge

#function to get the top movies

from django.db.models import Count
def top_movies(request):
    top_movies = Movie.objects.annotate(num_orders=Count('rentorderitems')).order_by('-num_orders')[:10]

#function to get the top customers
def top_customers(request):
    top_users = Customer.objects.values('id').annotate(count=Count('id')).order_by('count')[:10]
    return top_users


#function to track the revenues for day, month and year
#We would need to use the filter method which is applicable to days, month 
# and year. We would also need to use the sum from the aggregate function 
# to calculate the revenue for either of these options.

from django.db.models import Sum, F, ExpressionWrapper
from django.db.models.functions import ExtractMonth, ExtractDay, ExtractYear
def get_revenue_data(day, month, year):

    if RentOrder.PAYMENT_STATUS_CHOICES == 'C':
        #Using an expression wrapper to specifyu an output field because quantity is an integer field 
        # and unit_price is a decimal field so without an expression wrapper,
        # the code would throw an exception. 

        total = ExpressionWrapper(Sum(F('rentorderitem_set__quantity') * F('rentorderitem_set__unit_price')), output_field=DecimalField())

        monthly_revenue = RentOrder.objects.annotate(month=ExtractMonth('placed_at'))\
        .values('month').annotate(total_quantity_count=Sum('rentorderitem_set__quantity'), total=total)
        
        daily_revenue = RentOrder.objects.annotate(day=ExtractDay('placed_at'))\
        .values('month').annotate(total_quantity_count=Sum('rentorderitem_set__quantity'), total=total)
        yearly_revenue = RentOrder.objects.annotate(day=ExtractYear('placed_at'))\
        .values('month').annotate(total_quantity_count=Sum('rentorderitem_set__quantity'), total=total)
        

#Value objects would be important whenever we would want to pass an 
# expression like a number or a string.


#Function to calculate the top customers who have made orders

def get_top_customers(request):
    queryset = Customer.objects.annotate(orders_count=Count('rentorder'))


    #The ability to override the save method is something that may come in handy in the future when we want to override how objects are
    #saved by unpacking the validated data that we pass in through JSON and use that data by either associating it with another class by 
    # performing checks or adding some logic into it.

    def create(self, validated_data):
        movie = Movie(**validated_data)
        #adding a new field
        movie.posters = poster
        movie.save()
        return movie
    
    #We also have the ability to override how objects are updated, by updating the fields already in the object.
    def update(self, instance, validated_data):
        #instance is the default name django expects to look for no matter the object it is dealing with.
        #We use the get method to get the specific information of the object that we would need.
        instance.unit_price = validated_data.get('unit_price')
        instance.save()
        return instance
    

class MovieList(ListCreateAPIView):
    pass
    # # def get(self, request):
    # #     #eagerloading the movies with their genres to speed up queries.
    # #     queryset = Movie.objects.prefetch_related('genres').all()
    # #     #Returning all movies by iterating on it using the many keyword.
    # #     serializer = MovieSerializer(queryset, many=True, context={'request': request})
    # #     return Response(serializer.data)
    
    #  def post(self, request):
    # #     #Deserializing the JSON data object passed by the client into a python object
    # #     serializer = MovieSerializer(data=request.data)
    # #     #Validating the data in order to save it
         #  serializer.is_valid(raise_exception=True)
    #calling the save method in order to save the information passed in the
     # validated data dictionary into the database
    # #     serializer.save()
    # #     #Returning the validated data
    # #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    # #since most of the post and create operations are already encapsulated in the ListCreateApiView, all we
    # # would need are the queryset, serializer class and the serializer context if available.
    # # If we ever need to add logic, to the queryset or the serializer class we can the use the def get_queryset, 
    # # the get_ serializer_class or the get_serializer_context.
    # def get_queryset(self):
    #     return Movie.objects.prefetch_related('genres').all()
    
    
    # def get_serializer_class(self):
    #     return MovieSerializer
    
    # def get_serializer_context(self):
    #     return {'request': self.request}
    
    #But since we do not want to add extra logic, we can assign a query and a serializer class
    # to the queryset and serializer class variables.
    # queryset = Movie.objects.prefetch_related('genres').all()

    # serializer_class = MovieSerializer


    #We can use the Modelviewset to combine the logic for multiple related views
    #For instance, we can combine both the Movie list and the Movie Detail viewset into one.
    # 
    #The model viewset has the combination of all the mixins: Create, Retrieve, Update, Destroy, and List.
    # from rest_framework.viewsets import ModelViewSet
    #  

    # with this implementation, we can forgo the need to create a Movie List and detail classes
    # Only inclusing the queryset, Serializer class and any other additional logic here. 
    #class MovieViewSet(ModelViewSet):
    #   queryset = Movie.objects.all()
    #   serializer_class = MovieSerializer
    # 
    #   def get_serializer_context(self):
    #       return {'request': self.request} 

    #   def delete(self, request, pk):
    #        movie = get_object_or_404(Movie, pk)
    #        if movie.rentorderitems.count > 0:
    #        return Response({'error': 'Movie cannot be deleted because it is associated with a rent orderitem'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            # movie.delete()
            # return Response(status=status.HTTP_204_NO_CONTENT) 


    # # Function to override the queryset to allow for filtering.
    # def get_queryset(self):
    #     queryset = Movie.objects.prefetch_related('genres').all()
    #     genres_id = self.request.query_params.get('genres_id')
        
    #     #Getting the collection id that is in the query parameters and storing it.
    #     if genres_id is not None:
    #          #The genres field on the Movie model is a ManyToManyField which creates an intermediary table
    #          # to manage the relationship between Movie and Genre models. As a result, I cannot directly filter on genres_id
    #          # as it is not a field of the Movie model. 
    #          #To filter movies based on the genres_id provided in the query parameters, I need to use the correct field name 
    #          # for the genres relationship in the filter method. Since it's a ManyToManyField, 
    #          # I should use the double underscore notation to access the ID of the related Genre model.
    #         queryset = queryset.filter(genres__id=genres_id)