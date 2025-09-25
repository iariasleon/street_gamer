from django.urls import path
from . import views
from django.urls import path
from .views import PlayerLocationCreateView, PlaceListView

urlpatterns = [
    path('map/', views.map, name='map'),
    path('location/', PlayerLocationCreateView.as_view(), name='player-location'),
    path('places/', PlaceListView.as_view(), name='places-list'),
]
