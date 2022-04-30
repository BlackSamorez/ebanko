import json

from Ebanko import Ebanko

from flask import Flask, request, jsonify
from prometheus_flask_exporter.multiprocess import GunicornInternalPrometheusMetrics
from prometheus_client import Counter


app = Flask(__name__, static_url_path="")
metrics = GunicornInternalPrometheusMetrics(app)

model = Ebanko()

@app.route("/predict", methods=['POST'])
@metrics.gauge("api_in_progress", "requests in progress")
@metrics.counter("api_invocations_total", "number of invocations")
def predict():
    data = request.get_json(force=True)
    text = torch.tensor(data['data'])

    result = model(text)

    return jsonify({
        "toxified": result
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
