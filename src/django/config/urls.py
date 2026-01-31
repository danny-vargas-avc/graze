from django.urls import path
from . import views

urlpatterns = [
    path('all/', views.config_all, name='config-all'),
]
