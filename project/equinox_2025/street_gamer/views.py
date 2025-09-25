import folium

from django.shortcuts import render
from django.http import HttpResponse
from geopy.geocoders import Nominatim


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
