from flask import jsonify
from flask_app import app
from flask_app.models.achievement_state import AchievementState
from flask_app.services.steam_service import SteamService

TEST_APP_ID = 2060160  # The Farmer Was Replaced

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/api/state")
def get_state():
    steam = SteamService()
    state = steam.build_achievement_state(TEST_APP_ID)
    return jsonify(state)

@app.route("/api/event")
def get_event():
    return jsonify(AchievementState.load_event())