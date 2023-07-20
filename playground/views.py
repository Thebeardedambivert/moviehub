from django.forms import DecimalField
from django.shortcuts import render
from django.http import HttpResponse

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