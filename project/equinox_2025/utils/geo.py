import certifi
import ssl
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time

# Configurar SSL para usar certificados confiables
ssl_context = ssl.create_default_context(cafile=certifi.where())

# Inicializar el geolocalizador con SSL
geolocator = Nominatim(user_agent="_equinox_geo_street_game", ssl_context=ssl_context)

def localiza_poblacion(lat, lon):
    """
    Devuelve la poblacion y pais a partir de coordenadas.
    Maneeja timeouts y casos donde no hay ciudad
    """
    try:
        location = geolocator.reverse((lat, lon), language="es", timeout=10)
        if location and location.raw:
            address = location.raw.get("address", {})
            city = address.get("city") or address.get("town") or address.get("village")
            country = address.get("country")
            return city, country
        else:
            return None, None
    except GeocoderTimedOut:
        time.sleep(1)
        return localiza_poblacion(lat, lon)
    except Exception as e:
        print(f"Error: {e}")
        return None, None


# if __name__ == "__main__":
#     # #cuenca
#     # coordenadas="40.062648354024375, -2.128627199395899"
#     # madrid
#     # coordenadas="40.42543459832981, -3.6682371750965657"
#
#     coordenadas = [
#         (38.9161, -6.3437),  # Mérida, España
#         (40.4168, -3.7038),  # Madrid, España
#         (40.0626, -2.1286)    # Cuenca, España
#     ]
#
#     for lat, lon in coordenadas:
#         city, country = localiza_poblacion(lat, lon)
#         print(f"Coordenadas: ({lat}, {lon}) -> Ciudad: {city}, País: {country}")
