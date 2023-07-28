from typing import Any, List, Optional, Tuple
from django.contrib import admin, messages
from django.db.models import Count, F
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
#utility function to automatically render the url address 
# of the page that we want to reference. 
from django.urls import reverse
from django.utils.html import format_html, urlencode
from . import models

# Register your models here.



#Class to make a custom filter
class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            ('<3', 'Running out')
            ]
    
    #overriding queryset to gain access to the value chosen by the user.
    def queryset(self, request, queryset: QuerySet):
        if self.value() == '<3':
            return queryset.filter(inventory__lt=3)
        

#Filter to easily track the status of movie orders by customers.
class OrderStatusFilter(admin.SimpleListFilter):
    title = 'orderstatus'
    parameter_name = 'orderstatus'


    def lookups(self, request, model_admin):
        return [
            ('Collected', 'Collected'),
            ('Lost', 'Lost'),
            ('Returned', 'Returned')
        ]
    
    def queryset(self, request, queryset: QuerySet):
        if self.value() == 'Collected':
            queryset = models.RentOrder.objects.filter(order_status='ORDER_STATUS_COLLECTED')
            return queryset
        elif self.value() == 'Lost':
            queryset = models.RentOrder.objects.filter(order_status='ORDER_STATUS_LOST')
            return queryset
        elif self.value() == 'Returned':
            queryset = models.RentOrder.objects.filter(order_status='ORDER_STATUS_RETURNED')
            return queryset

        


@admin.register(models.Movie)
class MovieAdmin(admin.ModelAdmin):
    #Provides an autocompletion feature that allows for easier navigation.
    autocomplete_fields = ['genres']

    #Explicitly state the actions that we defined within the class.
    actions = ['clear_inventory']

    #list of fields we want displayed on the admin panel
    list_display = ['barcode', 'title', 'description', 'get_genres','inventory', 'daily_rental_rate', 'genres_list']

    #Fields that are allowed to be editable
    list_editable = ['title', 'description', 'daily_rental_rate']

    #Filter movies by their genres and when last they were updated
    list_filter = ['genres', 'last_updated', InventoryFilter]

    #limit the movies being shown on each page
    list_per_page = 10

    search_fields = ['title']

    #function to eagerload many to many related field, genres. And to 
    #provide a link to the genres admin page.
    @admin.display(ordering='genres')
    def genres_list(self, movie):
        url = (reverse('admin:hub_genre_changelist')
               + '?'
               + urlencode({'movie__id': str(movie.id)
                            }))

        return format_html( '<a href="{}">{} Genres</a>', url, movie.genres)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('genres')
            
    

    #decorator used to specify field used for ordering
    @admin.display(ordering='inventory_status')
    #function to keep track of the inventory status of the movies.
    def inventory_status(self, movie:models.Movie):
        if movie.inventory <= 3:
            return 'Running out'
        return 'In stock'

    #Rendering a specific field in the related genre table
    def get_genres(self, obj):
        return ", ".join([genre.title for genre in obj.genres.all()])
    
    @admin.action(description='Clear Inventory')
    def clear_inventory(self, request, queryset:QuerySet):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{updated_count} movies were successfully updated.',
            messages.ERROR
        )


@admin.register(models.Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['title']

    #We have to use searchfields when we are adding an auto complete 
    # field to a related Admin class as is the case between the movies 
    # and the genre admin classes. 
    search_fields = ['title']

    list_per_page = 10

    ordering = ['title']

    @admin.display(ordering='movies_count')
    def movies_count(self, genre):
        #Code to dynamically render and store the url of the html link.
        # We would also need to pass in a special argument (admin: app_model_page).
        url = (
            reverse('admin:hub_movie_changelist')
            + '?'
            #Query string parameter to enable filteration when rendering the url
            #for instance: genre__id=3. It is imprtant to note that this receives a 
            #dictionary because a querystring can contain multiple key value pairs.
            + urlencode({
                'genre__id': str(genre.id)
            }))
        #Code to include a html link to the movies admin page 
        # from the genres page.
        return format_html('<a href="{}">{}</a>', url, genre.movies_count)
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(movies_count=Count('movie'))


class RentOrderItemInline(admin.TabularInline):
    autocomplete_fields = ['movie']
    model = models.RentOrderItem
    extra = 0


@admin.register(models.RentOrder)
class RentOrderAdmin(admin.ModelAdmin):
    #Remember to add a custom filter so it would be easy to see the 
    #payments that are failed and payments that were completed.
    autocomplete_fields = ['customer']
    inlines = [RentOrderItemInline]
    list_display = ['id', 'rent_date', 'return_date', 'order_status', 'payment_status', 'customer']
    list_per_page = 30
    ordering = ['rent_date']
    list_filter = ['rent_date', 'return_date', OrderStatusFilter]
    list_select_related = ['customer']

#Class to include fields within the rentorder child relationship 
# in the CustomerAdmin form, which is its parent.
class RentOrderInline(admin.TabularInline):
    model = models.RentOrder

    #removes extra fields
    extra = 0


class AddressInline(admin.TabularInline):
    model = models.Address
    extra = 0

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    actions = ['block_user']
    inlines = [RentOrderInline, AddressInline]
    list_display = ['first_name', 'last_name']
    list_per_page = 10
    list_select_related = ['user']
    ordering = ['user__first_name', 'user__last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    #Remember to add an age validator for customers where if they are not
    #18, they cannot rent some movies. We should add an age field to the 
    #customer model and use either the MinValueValidator and the MaxValueValidator 
    #to implement it. 

    #Function to enable the blocking of a user by updating the permissions 
    # in the default queryset.
    @admin.action(description='Block user')
    def block_user(self, request, queryset: QuerySet):
        queryset.update(is_active=False)
        self.message_user(
            request,
            "User was successfully blocked."
        )



@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['movie', 'name', 'description', 'date']
    ordering = ['movie']
    list_per_page = 10

    #Remember to add data validation for the content of the review, 
    # to only accept words and numbers not just numbers.
    # To achieve this we can use the regex validator 
    # where we ensure that we have a mixture of both numbers and letters,
    # or we can use a custom validator.