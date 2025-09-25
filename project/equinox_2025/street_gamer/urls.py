from . import views
from .views import PlayerLocationCreateView, PlaceListView
from django.urls import path
from django.http import HttpResponse

def index(request):
    return HttpResponse("API Street Gamer: usa /location/ o /places/")

urlpatterns = [
    path('map/', views.map, name='map'),
    path('location/', PlayerLocationCreateView.as_view(), name='player-location'),
    path('places/', PlaceListView.as_view(), name='places-list'),
    path('', index),
]
