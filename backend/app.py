from flask import Flask, request, jsonify
from flask_cors import CORS
from services.weather_service import get_weather_data, get_coordinates, clean_old_cache
import numpy as np
import psycopg2
from datetime import datetime, timedelta
import json
import os
import threading
import time

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    dbname=os.getenv("DB_NAME")
)


app = Flask(__name__)
CORS(app)

def periodic_cache_cleanup(interval_sec, conn):
    while True:
        try:
            clean_old_cache(conn)
            print("Cache cleaned")
        except Exception as e:
            print(f"Error cleaning cache: {e}")
        time.sleep(interval_sec)


def convert_np_types(obj):
    if isinstance(obj, dict):
        return {k: convert_np_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_np_types(i) for i in obj]
    elif isinstance(obj, np.generic):
        return obj.item()
    else:
        return obj

@app.route('/api/weather', methods=['GET'])
def weather_api():
    city = request.args.get('city')
    country = request.args.get('country')

    if not city and not country:
        return jsonify({"error": "Please enter at least a city or country name"}), 400

    latitude, longitude, city, country = get_coordinates(city, country)
    if latitude is None or longitude is None:
        return jsonify({"error": "Location not found. Try again."}), 404

    with conn.cursor() as cursor:
        query = """
            SELECT weather_data, timestamp 
            FROM weather_cache 
            WHERE LOWER(city) = LOWER(%s) AND LOWER(country) = LOWER(%s) 
            ORDER BY timestamp DESC LIMIT 1;
        """
        cursor.execute(query, (city, country))
        row = cursor.fetchone()

        if row:
            weather_data, timestamp = row
            if datetime.utcnow() - timestamp < timedelta(minutes=20):
                return jsonify(weather_data)  

    try:
        data = get_weather_data(latitude, longitude)
    except Exception as e:

        if row:
            return jsonify({
                "warning": "Using cached data due to external API failure.",
                "data": weather_data
            })
        else:
            return jsonify({"error": "Weather data not available and no cached data found."}), 503

    if not data:
        if row:
            return jsonify({
                "warning": "Using cached data because external API returned no data.",
                "data": weather_data
            })
        else:
            return jsonify({"error": "Weather data not available"}), 503

    cleaned_data = convert_np_types(data)

    with conn.cursor() as cursor:
        insert_query = """
            INSERT INTO weather_cache (city, country, weather_data, timestamp)
            VALUES (%s, %s, %s, %s);
        """
        cursor.execute(insert_query, (
            city.lower(),
            country.lower(),
            json.dumps(cleaned_data),
            datetime.utcnow()
        ))
        conn.commit()

    return jsonify(cleaned_data)

if __name__ == '__main__':
    cleanup_thread = threading.Thread(target=periodic_cache_cleanup, args=(1200, conn), daemon=True)
    cleanup_thread.start()


    app.run(debug=False, host='0.0.0.0', port=5000)
