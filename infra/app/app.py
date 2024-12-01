from flask import Flask, request, jsonify
from collections import deque
import logging

app = Flask(__name__)

# Настроим логирование
logging.basicConfig(level=logging.INFO)

# Храним последние 10 запросов
recent_requests = deque(maxlen=10)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    # Логируем тело запроса
    app.logger.info(f"Request body: {data}")

    # Извлекаем необходимые данные из вложенных структур
    try:
        ip = data.get("source", {}).get("address", "unknown")
        response_code = int(data.get("http", {}).get("response", {}).get("status_code", 0))
        bytes_sent = int(data.get("http", {}).get("response", {}).get("body", {}).get("bytes", 0))
        url = data.get("url", {}).get("original", "/")
        method = data.get("http", {}).get("request", {}).get("method", "UNKNOWN")
    except ValueError:
        return jsonify({"error": "Invalid data format"}), 400

    # Определяем, является ли запрос аномальным
    is_anomalous = response_code > 400

    # Добавляем запрос в список последних запросов
    recent_requests.append({
        "ip": ip,
        "method": method,
        "url": url,
        "response": response_code,
        "bytes": bytes_sent,
        "anomalous": is_anomalous
    })

    return jsonify({
        "ip": ip,
        "method": method,
        "url": url,
        "response": response_code,
        "bytes": bytes_sent,
        "anomalous": is_anomalous
    })

@app.route('/requests', methods=['GET'])
def get_recent_requests():
    return jsonify({"recent_requests": list(recent_requests)})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")