from flask import Flask, request, jsonify
from flask_cors import CORS
from services.weather_service import get_weather_data, get_coordinates  
import numpy as np

app = Flask(__name__)
CORS(app)  # מאפשר קריאות React מדומיין אחר

def convert_np_types(obj):
    if isinstance(obj, dict):
        return {k: convert_np_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_np_types(i) for i in obj]
    elif isinstance(obj, np.generic):  # כל טיפוס numpy בסיסי
        return obj.item()
    else:
        return obj

@app.route('/api/weather', methods=['GET'])
def weather_api():
    city = request.args.get('city')
    country = request.args.get('country')

    if not city and not country:
        return jsonify({"error": "Please enter at least a city or country name"}), 400

    latitude, longitude, country, city = get_coordinates(city, country)
    if latitude is None or longitude is None:
        return jsonify({"error": "Location not found. Try again."}), 404

    data = get_weather_data(latitude, longitude)
    if not data:
        return jsonify({"error": "Weather data not available"}), 503

    cleaned_data = convert_np_types(data)  # המרה לכל טיפוס רגיל

    return jsonify(cleaned_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
