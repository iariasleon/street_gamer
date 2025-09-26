import json

from openai import OpenAI
from street_gamer.utils.tools import localiza_poblacion


JSON_TEMPLATE = """
            {
              "poblacion": "NOMBRE",
              "coordenadas": {
                "latitud": XX.XXXX,
                "longitud": YY.YYYY
              },
              "lugares_interes": [
                {
                  "nombre": "Nombre del lugar",
                  "coordenadas": { "latitud": XX.XXXX, "longitud": YY.YYYY },
                  "informacion": "Descripción breve.",
                  "pregunta": "Texto de la pregunta",
                  "respuestas": {
                    "respuesta_correcta": "Texto de la respuesta correcta",
                    "respuestas_incorrectas": [
                      "Respuesta fake 1",
                      "Respuesta fake 2",
                      "Respuesta fake 3"
                    ]
                  }
                }
              ]
            }
        """


def city_quiz_ia(lat, lon):
    """
    Genera una lista de lugares de interés en una ciudad dada sus coordenadas.
    """

    city, country = localiza_poblacion(lat, lon)

    client = OpenAI(
        api_key="xxxx" ) # Reemplaza con tu clave de API de OpenAI)

    # ejemplo coordenadas="(48.8566, 2.3522)  París, Francia"
    coordenadas = f"({lat}, {lon})  {city}, {country}"

    prompt = """
        Identifica la población (municipio, ciudad o pueblo) a la que pertenecen estas coordenadas "{coordenadas}".
        Elabora una lista de al menos 10 lugares de interés, monumentos, rincones curiosos o puntos destacados enestas  coordenadas "{coordenadas}" que se puedan visitar en dicha población o en sus alrededores cercanos.
        Para cada lugar, incluye:
        -nombre
        -coordenadas (latitud y longitud aproximadas)
        -informacion (breve descripción o detalle interesante)
        -pregunta (curiosidad que pueda responderse visitando el lugar)
        -respuestas → objeto con:
        -- respuesta_correcta
        -- respuestas_incorrectas (5 respuestas, realistas pero falsas)
        la respuesta debe seguir el siguiente formato JSON: {json_template}
        """.format(coordenadas=coordenadas, json_template=JSON_TEMPLATE)

    #print(f"PROMP USADO>> \n\r {prompt}")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un asistente que devuelve solo JSON válido."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )


    city_quiz = (response.choices[0].message.content).replace("json", "", 1)
       
    print("----------------------------------------------------------")
    print("PEPEPE: \n",city_quiz)
    print("PEPEPE type: \n",type(city_quiz))
    print("----------------------------------------------------------")
       
    city_quiz_json = json.loads(city_quiz)
    #print(response.choices[0].message.content)
    city = city_quiz_json['poblacion'].replace(",", "_").replace(" ", "_").lower()
    with open(f"street_gamer/cities/city_quiz_{city}.json", "w") as f:
        f.write(city_quiz)



# if __name__ == "__main__":
# #jerez: 38.31871039885761, -6.771057306831485
#
#     coordenadas = [
#         (38.3187, -6.7710),  # JerezCa, España
#     ]
#
#     for lat, lon in coordenadas:
#         city_quiz_ia(lat, lon)
