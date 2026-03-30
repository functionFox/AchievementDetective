from flask import jsonify
from flask_app import app
from flask_app.models.achievement_state import AchievementState

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/api/state")
def get_state():
    return jsonify(AchievementState.load_state())

@app.route("/api/event")
def get_event():
    return jsonify(AchievementState.load_event())