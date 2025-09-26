import folium
import math
import json
import os
import random

from .serializers import PlayerLocationSerializer, PlaceSerializer
from .models import PlayerLocation, Place, PlayerPlaceStatus

from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from rest_framework.response import Response
from rest_framework import generics, permissions, authentication
from rest_framework.authentication import TokenAuthentication

from street_gamer.utils.tools import read_json_from_file, localiza_poblacion
from street_gamer.utils.ia_queries import city_quiz_ia


# # Listar todos los lugares (para mostrar retos)
# class PlaceListView(generics.ListAPIView):
#     queryset = Place.objects.all()
#     serializer_class = PlaceSerializer
#     permission_classes = [permissions.IsAuthenticated]


@csrf_exempt
def location_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        # Guardamos en la sesión
        request.session['latitude'] = latitude
        request.session['longitude'] = longitude

        return JsonResponse({"ok": True})
    return JsonResponse({"error": "Método no permitido"}, status=405)



def map(request):
    latitude = request.session.get('latitude', 41.9028)  # fallback a Roma
    longitude = request.session.get('longitude', 12.4964)    

    city = localiza_poblacion(latitude, longitude)[0]   
    
    # Add map
    m = folium.Map(location=[latitude, longitude], zoom_start=14)
    folium.Marker([latitude, longitude], popup=city, tooltip=city).add_to(m)

    # Add points
    city_file = city.replace(",", "_").replace(" ", "_").lower()
    file_path = f"street_gamer/cities/city_quiz_{city_file}.json"
    if not os.path.exists(file_path):
        city_quiz_ia(latitude, longitude)    
    points = read_json_from_file(file_path)
    for p in points["lugares_interes"]:
        folium.Marker(
            [p["coordenadas"]["latitud"], p["coordenadas"]["longitud"]],
            popup=p["nombre"],
            tooltip=p["nombre"],
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)

    # # Generate questions
    # questions = []
    # for lugar in points["lugares_interes"]:
    #     pregunta = lugar["pregunta"]
    #     respuesta_correcta = lugar["respuestas"]["respuesta_correcta"]
    #     respuestas_incorrectas = lugar["respuestas"]["respuestas_incorrectas"]
    #     opciones = [respuesta_correcta] + random.sample(respuestas_incorrectas, 2)
    #     random.shuffle(opciones)  # Shuffle options

    #     questions.append({
    #         "pregunta": pregunta,
    #         "opciones": opciones,
    #         "respuesta_correcta": respuesta_correcta
    #     })

    m = m._repr_html_()
    return render(request, "map.html", {"map": m, "ciudad": city})


# def haversine(lat1, lon1, lat2, lon2):
#     # Radio de la Tierra en metros
#     R = 6371000
#     phi1 = math.radians(lat1)
#     phi2 = math.radians(lat2)
#     delta_phi = math.radians(lat2 - lat1)
#     delta_lambda = math.radians(lon2 - lon1)

#     a = math.sin(delta_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(delta_lambda/2)**2
#     c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))

#     return R * c  # distancia en metros



# class PlayerLocationCreateView(generics.CreateAPIView):
#     queryset = PlayerLocation.objects.all()
#     serializer_class = PlayerLocationSerializer
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = [permissions.IsAuthenticated]

#     def create(self, request, *args, **kwargs):
#         # Obtener serializer y validar
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         # Guardar ubicación
#         player_location = serializer.save(player=request.user)

#         # Comprobar lugares alcanzados
#         reached_places = []
#         for place in Place.objects.all():
#             dist = haversine(
#                 player_location.latitude,
#                 player_location.longitude,
#                 place.latitude,
#                 place.longitude
#             )
#             if dist <= place.radius:
#                 reached_places.append({
#                     "place": place.name,
#                     "question": place.question,
#                     "distance_m": round(dist, 2)
#                 })
#                 # Guardar estado completado
#                 status, created = PlayerPlaceStatus.objects.get_or_create(
#                     player=request.user,
#                     place=place,
#                     defaults={'completed': True, 'completed_at': timezone.now()}
#                 )
#                 if not created and not status.completed:
#                     status.completed = True
#                     status.completed_at = timezone.now()
#                     status.save()

#         # Preparar respuesta
#         response_data = serializer.data
#         response_data["reached_places"] = reached_places
#         return Response(response_data)


