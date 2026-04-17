from flask import jsonify, request
from flask_app import app
from flask_app.models.achievement_state import AchievementState
from flask_app.services.achievement_service import AchievementService
from flask_app.services.db_service import set_setting
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

@app.route("/api/achievements", methods=["GET"])
def get_achievements():
    appid = request.args.get("appid", type=int)

    if appid:
        state = AchievementService.refresh_game_achievements(appid)
        return jsonify(state)

    return jsonify(AchievementState.load_state())

@app.route("/api/select-game", methods=["POST"])
def select_game():
    data = request.get_json(silent=True) or {}
    app_id = data.get("app_id")

    if not app_id:
        return jsonify({"error": "Missing app_id"}), 400

    set_setting("active_appid", str(app_id))
    state = AchievementService.refresh_game_achievements(app_id)

    return jsonify(state)