import folium
import math

from django.shortcuts import render
from django.http import HttpResponse
from geopy.geocoders import Nominatim

from rest_framework import generics, permissions
from .serializers import PlayerLocationSerializer, PlaceSerializer

from django.utils import timezone
from .models import PlayerPlaceStatus
from .models import Place, PlayerLocation



# Listar todos los lugares (para mostrar retos)
class PlaceListView(generics.ListAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [permissions.IsAuthenticated]

def map(request):
    city = request.GET.get("ciudad", "Madrid")
    geolocator = Nominatim(user_agent="mi_app_map")

    try:
        location = geolocator.geocode(city)
        lat, lng = location.latitude, location.longitude
    except Exception:
        city = "Madrid"
        lat, lng = 40.4165, -3.70256

    # Add map
    m = folium.Map(location=[lat, lng], zoom_start=14)
    folium.Marker([lat, lng], popup=city, tooltip=city).add_to(m)


    m = m._repr_html_()
    return render(request, "map.html", {"map": m, "ciudad": city})



def haversine(lat1, lon1, lat2, lon2):
    # Radio de la Tierra en metros
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(delta_lambda/2)**2
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c  # distancia en metros




class PlayerLocationCreateView(generics.CreateAPIView):
    queryset = PlayerLocation.objects.all()
    serializer_class = PlayerLocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Guardar la ubicación
        player_location = serializer.save(player=self.request.user)

        # Comprobar lugares
        for place in Place.objects.all():
            distance = haversine(player_location.latitude, player_location.longitude,
                                 place.latitude, place.longitude)
            if distance <= place.radius:
                # marcar completado
                status, created = PlayerPlaceStatus.objects.get_or_create(
                    player=self.request.user,
                    place=place,
                    defaults={'completed': True, 'completed_at': timezone.now()}
                )
                if not created and not status.completed:
                    status.completed = True
                    status.completed_at = timezone.now()
                    status.save()
