import folium
import math

from .serializers import PlayerLocationSerializer, PlaceSerializer

from django.utils import timezone
from .models import PlayerLocation, Place, PlayerPlaceStatus
from rest_framework import generics, permissions, authentication
from rest_framework.authentication import TokenAuthentication

from django.shortcuts import render
from rest_framework.response import Response
from street_gamer.utils.tools import read_json_from_file
import random


# Listar todos los lugares (para mostrar retos)
class PlaceListView(generics.ListAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [permissions.IsAuthenticated]


def map(request):
    city = request.GET.get("ciudad", "Jerez de los Caballeros")
    city_file = city.replace(",", "_").replace(" ", "_").lower()
    points = read_json_from_file(f"street_gamer/cities/city_quiz_{city_file}.json")
    city = points["poblacion"]
    lat, lng = points["coordenadas"]["latitud"], points["coordenadas"]["longitud"]

    # Add map
    m = folium.Map(location=[lat, lng], zoom_start=14)
    folium.Marker([lat, lng], popup=city, tooltip=city).add_to(m)

    # Add points
    for p in points["lugares_interes"]:
        folium.Marker(
            [p["coordenadas"]["latitud"], p["coordenadas"]["longitud"]],
            popup=p["nombre"],
            tooltip=p["nombre"],
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)

    # Generate questions
    questions = []
    for lugar in points["lugares_interes"]:
        pregunta = lugar["pregunta"]
        respuesta_correcta = lugar["respuestas"]["respuesta_correcta"]
        respuestas_incorrectas = lugar["respuestas"]["respuestas_incorrectas"]
        opciones = [respuesta_correcta] + random.sample(respuestas_incorrectas, 2)
        random.shuffle(opciones)  # Shuffle options

        questions.append({
            "pregunta": pregunta,
            "opciones": opciones,
            "respuesta_correcta": respuesta_correcta
        })

    m = m._repr_html_()
    return render(request, "map.html", {"map": m, "ciudad": city, "questions": questions})


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
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Obtener serializer y validar
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Guardar ubicación
        player_location = serializer.save(player=request.user)

        # Comprobar lugares alcanzados
        reached_places = []
        for place in Place.objects.all():
            dist = haversine(
                player_location.latitude,
                player_location.longitude,
                place.latitude,
                place.longitude
            )
            if dist <= place.radius:
                reached_places.append({
                    "place": place.name,
                    "question": place.question,
                    "distance_m": round(dist, 2)
                })
                # Guardar estado completado
                status, created = PlayerPlaceStatus.objects.get_or_create(
                    player=request.user,
                    place=place,
                    defaults={'completed': True, 'completed_at': timezone.now()}
                )
                if not created and not status.completed:
                    status.completed = True
                    status.completed_at = timezone.now()
                    status.save()

        # Preparar respuesta
        response_data = serializer.data
        response_data["reached_places"] = reached_places
        return Response(response_data)


