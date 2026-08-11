from flask import Flask, jsonify, render_template, request

from agent import create_itinerary, replan_itinerary

app = Flask(__name__)


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/api/plan-trip")
def plan_trip():
    try:
        payload = request.get_json(force=True) or {}
        result = create_itinerary(payload)
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.post("/api/replan")
def replan_trip():
    try:
        payload = request.get_json(force=True) or {}
        result = replan_itinerary(payload)
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
