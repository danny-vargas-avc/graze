from django.urls import path
from .views import DishListView, DishDetailView, RestaurantListView, RestaurantDetailView, StatsView, DataFlagCreateView

urlpatterns = [
    path('dishes', DishListView.as_view(), name='dish-list'),
    path('dishes/<int:pk>', DishDetailView.as_view(), name='dish-detail'),
    path('restaurants', RestaurantListView.as_view(), name='restaurant-list'),
    path('restaurants/<slug:slug>', RestaurantDetailView.as_view(), name='restaurant-detail'),
    path('stats', StatsView.as_view(), name='stats'),
    path('flags', DataFlagCreateView.as_view(), name='flag-create'),
]
