from flask import jsonify, request
from flask_app import app
from flask_app.models.achievement_state import AchievementState
from flask_app.services.achievement_service import AchievementService
from flask_app.services.db_service import set_setting, get_setting, get_game_by_app_id, get_games, upsert_games
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

@app.route("/api/active-game", methods=["GET"])
def get_active_game():
    active_app_id = get_setting("active_appid")

    if not active_app_id:
        return jsonify({"active_app_id": None, "game": None})

    game = get_game_by_app_id(str(active_app_id))

    return jsonify({
        "active_app_id": active_app_id,
        "game": game
    })

@app.route("/api/games", methods=["GET"])
def get_games_route():
    games = get_games()

    if not games:
        steam = SteamService()
        owned = steam.get_owned_games()
        raw_games = owned.get("response", {}).get("games", [])

        normalized_games = [
            {
                "app_id": str(game["appid"]),
                "name": game["name"],
            }
            for game in raw_games
            if game.get("appid") is not None and game.get("name")
        ]

        upsert_games(normalized_games)
        games = get_games()

    return jsonify(games)