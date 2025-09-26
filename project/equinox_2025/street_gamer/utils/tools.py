import json
from pathlib import Path

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


def read_json_from_file(path):
    """Return JSON file read from a given path.

    :param path: dir where to read the file
    :return: dict with the info
    """
    file = Path(path)
    if not file.is_file():
        raise IOError(f"File {path} could not be found")
    try:
        return json.loads(file.read_text(encoding="utf8"))
    except ValueError as error:
        raise ValueError(f"Decoding file {path} to JSON failed") from error
