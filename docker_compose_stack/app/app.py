import json
import time

import requests
from datetime import datetime
from flask import Flask, Response, render_template

app = Flask(__name__, template_folder=".")
app.debug = True
app.testing = True


@app.route("/")
def home_page():
    return render_template("index.html")


@app.route("/chart-data")
def chart_data():
    def get_sensor_data():
        while True:
            # Read latest 5 computed values from stream_aggregator Lambda
            r = json.loads(requests.get("http://greengrass:8181/api/v1/aggregate").text)
            # r = json.loads(requests.get("http://localhost:8181/api/v1/aggregate").text)
            json_data = []
            for dataset in r:
                json_data.append(
                    {
                        "time": datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "device_id": dataset["device_id"],
                        "current_voltage": dataset["current_voltage"],
                        "time_left": dataset["time_left"],
                    }
                )
            yield f"data:{json.dumps(json_data)}\n\n"
            time.sleep(5)

    return Response(get_sensor_data(), mimetype="text/event-stream")


if __name__ == "__main__":
    # port mapped via Docker compose
    app.run(host="0.0.0.0", port=5000, debug=True)
