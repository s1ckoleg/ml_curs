import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import deque
import logging

import joblib

from model.get_geolocation import get_geolocation

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
logging.basicConfig(level=logging.INFO)
recent_requests = deque(maxlen=10)
UNKNOWN = 'UNKNOWN'

clf = joblib.load('random_forest_model.pkl')
scaler = joblib.load('scaler.pkl')

ip_encoder = joblib.load('ip_encoder.pkl')
method_encoder = joblib.load('method_encoder.pkl')
country_encoder = joblib.load('country_encoder.pkl')
city_encoder = joblib.load('city_encoder.pkl')

for encoder in [ip_encoder, method_encoder, country_encoder, city_encoder]:
    encoder.classes_ = np.append(encoder.classes_, UNKNOWN)


def safe_transform(encoder, value):
    if value in encoder.classes_:
        return encoder.transform([value])[0]
    else:
        return encoder.transform([UNKNOWN])[0]

@app.route('/analyze', methods=['OPTIONS'])
def handle_options():
    response = Flask.Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Authorization'
    return response


@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    app.logger.info(f"Request body: {data}")

    try:
        ip = data.get("source", {}).get("address", UNKNOWN)
        response_code = int(data.get("http", {}).get("response", {}).get("status_code", 0))
        size = int(data.get("http", {}).get("response", {}).get("body", {}).get("bytes", 0))
        url = data.get("url", {}).get("original", "/")
        method = data.get("http", {}).get("request", {}).get("method", UNKNOWN)
        timestamp = data.get("timestamp", UNKNOWN)

        country, city = get_geolocation(ip)

        req = {
            "ip": ip,
            "method": method,
            "url": url,
            "status": response_code,
            "size": size,
            "datetime": timestamp,
            "country": country,
            "city": city,
        }

        recent_requests.append(req)
        df = pd.DataFrame(recent_requests)

        df['datetime'] = pd.to_datetime(df['datetime'], format='%d/%b/%Y:%H:%M:%S %z')
        print(df['datetime'])
        df['hour'] = df['datetime'].dt.hour  # Hour of request
        df['request_rate'] = df.groupby('ip')['ip'].transform('count')  # Requests per IP

        ip_encoded = safe_transform(ip_encoder, req['ip'])
        method_encoded = safe_transform(method_encoder, req['method'])
        country_encoded = safe_transform(country_encoder, req['country'])
        city_encoded = safe_transform(city_encoder, req['city'])

        df['ip_encoded'] = ip_encoded
        df['method_encoded'] = method_encoded
        df['country_encoded'] = country_encoded
        df['city_encoded'] = city_encoded

        feature_columns = ['ip_encoded', 'method_encoded', 'size', 'request_rate', 'hour', 'country_encoded', 'city_encoded']
        X = df[feature_columns]

        X_scaled = scaler.transform(X)

        prediction = clf.predict(X_scaled)

        result = {'is_anomaly': int(prediction[0])}

        app.logger.info(f"Response: {result}")

        return jsonify(result)
    except ValueError:
        return jsonify({"error": "Invalid data format"}), 400

@app.route('/requests', methods=['GET'])
def get_recent_requests():
    return jsonify({"recent_requests": list(recent_requests)})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=3000)
