from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
import polyline
from flask_cors import CORS  # <- Importamos CORS

load_dotenv()
app = Flask(__name__)
CORS(app, origins=["https://gps-profinalraulciriacocastillo-3601ssj.onrender.com"])  # <- Dominio correcto

ORS_API_KEY = os.getenv("ORS_API_KEY")
ORS_URL = "https://api.openrouteservice.org/v2/directions"

CONSUMO_POR_KM = {"Automóvil": 0.12, "Bicicleta": 0.00, "A pie": 0.00}
PRECIO_GASOLINA_POR_LITRO = 24.00

ubicaciones_cache = {}

def obtener_coordenadas(texto):
    if texto in ubicaciones_cache:
        return ubicaciones_cache[texto]

    respuesta = requests.get(
        "https://api.openrouteservice.org/geocode/autocomplete",
        params={"api_key": ORS_API_KEY, "text": texto}
    ).json()

    if respuesta.get("features"):
        coordenadas = respuesta["features"][0]["geometry"]["coordinates"]
        ubicaciones_cache[texto] = coordenadas  
        return coordenadas
    return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/buscar_lugar")
def buscar_lugar():
    q = request.args.get("q")
    if not q:
        return jsonify([])

    respuesta = requests.get(
        "https://api.openrouteservice.org/geocode/autocomplete",
        params={"api_key": ORS_API_KEY, "text": q}
    ).json()

    lugares = [
        {"label": lugar["properties"]["label"], "coordinates": lugar["geometry"]["coordinates"]}
        for lugar in respuesta.get("features", [])
    ]

    return jsonify(lugares)

@app.route("/ruta", methods=["POST"])
def calcular_ruta():
    tipo_transporte = request.form.get("transporte")
    origen_texto = request.form.get("origen")
    destino_texto = request.form.get("destino")

    origen_coord = obtener_coordenadas(origen_texto)
    destino_coord = obtener_coordenadas(destino_texto)

    if not origen_coord or not destino_coord:
        return jsonify({"error": "Ubicación no encontrada"}), 400

    perfil = {
        "Automóvil": "driving-car",
        "Bicicleta": "cycling-regular",
        "A pie": "foot-walking"
    }.get(tipo_transporte, "driving-car")

    coords = [[origen_coord[0], origen_coord[1]], [destino_coord[0], destino_coord[1]]]
    headers = {"Authorization": ORS_API_KEY, "Content-Type": "application/json"}
    body = {"coordinates": coords, "instructions": True}

    response = requests.post(f"{ORS_URL}/{perfil}", json=body, headers=headers)
    
    if response.status_code != 200:
        return jsonify({"error": "Error al conectarse a la API de rutas"}), 500

    data = response.json()

    try:
        distancia_real = round(data["routes"][0]["summary"]["distance"] / 1000, 2)
        duracion_segundos = data["routes"][0]["summary"]["duration"]
        horas = int(duracion_segundos // 3600)
        minutos = int((duracion_segundos % 3600) // 60)

        gasolina_litros = round(distancia_real * CONSUMO_POR_KM[tipo_transporte], 2)
        costo_gasolina = round(gasolina_litros * PRECIO_GASOLINA_POR_LITRO, 2)

        velocidad_recomendada = round(distancia_real / ((horas + minutos / 60) or 1), 2)

        ruta_codificada = data["routes"][0]["geometry"]
        coordenadas_decodificadas = polyline.decode(ruta_codificada)

        ruta_geojson = {
            "type": "LineString",
            "coordinates": [[lng, lat] for lat, lng in coordenadas_decodificadas]
        }

        instrucciones = [
            f"{step['instruction']} en {step.get('name', 'Calle desconocida')} - {round(step['distance'] / 1000, 2)} km restantes"
            for step in data["routes"][0]["segments"][0]["steps"]
        ]

    except KeyError:
        return jsonify({"error": "Error al obtener datos de la API"}), 500

    respuesta = jsonify({
        "distancia_real": distancia_real,
        "duracion_horas": horas,
        "duracion_minutos": minutos,
        "gasolina_litros": gasolina_litros,
        "costo_gasolina": costo_gasolina,
        "ruta_geojson": ruta_geojson,
        "instrucciones": instrucciones,
        "velocidad_recomendada": velocidad_recomendada
    })

    respuesta.headers["Access-Control-Allow-Origin"] = "https://gps-profinalraulciriacocastillo-3601.onrender.com"  # <- Ajuste extra para CORS
    return respuesta

if __name__ == "__main__":
    app.run(debug=True)
