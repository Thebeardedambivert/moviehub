from django.urls import include, path
from rest_framework_nested import routers
from .views import CartViewSet, CartItemViewSet, CustomerViewSet, MovieViewSet, GenreViewSet, RentOrderViewSet, ReviewViewset

#Creating and registering the parent router in router and in router.urls we
# would have access to movie-list and movie-detail lookup fields. 
router = routers.DefaultRouter()
router.register('movies', MovieViewSet, basename='movies')
router.register('genres', GenreViewSet)
router.register('carts', CartViewSet, basename='carts')
router.register('customers', CustomerViewSet)
router.register('rentorders', RentOrderViewSet)

#Creating a parent router, movies, for the child router using the parent router, the parent prefix for the
# child resource and the lookup parameter for the child resource 
movies_router = routers.NestedDefaultRouter(router, 'movies', lookup='movie')
#Registering the child resource with the name, and the basename to be used to generate the url patterns.
movies_router.register('reviews', ReviewViewset, basename='movie-reviews')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', CartItemViewSet, basename='cart-items')





urlpatterns = [
    path('', include(router.urls)),
    path('', include(movies_router.urls)),
    path('', include(carts_router.urls)),
]
