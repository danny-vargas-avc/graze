from django.urls import path
from .views import (
    DishListView, DishDetailView,
    RestaurantListView, RestaurantDetailView,
    StatsView, DataFlagCreateView,
    LocationListView, LocationDetailView, LocationFlagCreateView,
    ByoComponentListView,
)

urlpatterns = [
    path('dishes', DishListView.as_view(), name='dish-list'),
    path('dishes/<int:pk>', DishDetailView.as_view(), name='dish-detail'),
    path('restaurants', RestaurantListView.as_view(), name='restaurant-list'),
    path('restaurants/<slug:slug>', RestaurantDetailView.as_view(), name='restaurant-detail'),
    path('locations', LocationListView.as_view(), name='location-list'),
    path('locations/<int:pk>', LocationDetailView.as_view(), name='location-detail'),
    path('stats', StatsView.as_view(), name='stats'),
    path('flags', DataFlagCreateView.as_view(), name='flag-create'),
    path('location-flags', LocationFlagCreateView.as_view(), name='location-flag-create'),
    path('restaurants/<slug:slug>/byo', ByoComponentListView.as_view(), name='byo-components'),
]
