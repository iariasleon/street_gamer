import folium

from django.shortcuts import render
from django.http import HttpResponse
from geopy.geocoders import Nominatim

from street_gamer.utils.tools import read_json_from_file


def map(request):
    city = request.GET.get("ciudad", "merida extremadura")
    city_file = city.replace(",", "_").replace(" ", "_").lower()
    points = read_json_from_file(f"street_gamer/cities/{city_file}.json")
    city = points["poblacion"]
    lat, lng = points["coordenadas"]["latitud"], points["coordenadas"]["longitud"]

    # Add map
    m = folium.Map(location=[lat, lng], zoom_start=14)
    folium.Marker([lat, lng], popup=city, tooltip=city).add_to(m)

    # add points
    for p in points["lugares_interes"]:
        print(p["coordenadas"])
        folium.Marker(
            [p["coordenadas"]["latitud"], p["coordenadas"]["longitud"]],
            popup=p["nombre"],
            tooltip=p["nombre"],
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)

    m = m._repr_html_()
    return render(request, "map.html", {"map": m, "ciudad": city})
