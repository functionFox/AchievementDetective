import time

from flask import jsonify, request
from flask_app import app
from flask_app.models.achievement_state import AchievementState
from flask_app.services.achievement_service import AchievementService
from flask_app.services.db_service import (
    set_setting,
    get_setting,
    get_game_by_app_id,
    get_games,
    upsert_games,
    get_achievement_state_by_app_id
)
from flask_app.services.steam_service import SteamService

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/api/state")
def get_state():
    active_app_id = get_setting("active_appid")

    if not active_app_id:
        return jsonify(AchievementState.load_state())

    cached_state = get_achievement_state_by_app_id(str(active_app_id))

    if cached_state is not None:
        return jsonify(cached_state)

    state = AchievementService.refresh_game_achievements(active_app_id)
    return jsonify(state)

@app.route("/api/event")
def get_event():
    return jsonify(AchievementState.load_event())

@app.route("/api/achievements", methods=["GET"])
def get_achievements():
    appid = request.args.get("appid", type=int)

    if appid:
        cached_state = get_achievement_state_by_app_id(str(appid))

        if cached_state is not None:
            return jsonify(cached_state)

        state = AchievementService.refresh_game_achievements(appid)
        return jsonify(state)

    return jsonify(AchievementState.load_state())

@app.route("/api/refresh-achievements", methods=["POST"])
def refresh_achievements():
    data = request.get_json(silent=True) or {}
    app_id = data.get("app_id")

    if not app_id:
        app_id = get_setting("active_appid")

    if not app_id:
        return jsonify({"error": "Missing app_id"}), 400

    state = AchievementService.refresh_game_achievements(app_id)
    return jsonify(state)

@app.route("/api/select-game", methods=["POST"])
def select_game():
    data = request.get_json(silent=True) or {}
    app_id = data.get("app_id")
    display_mode = data.get("display_mode")
    text_color = data.get("text_color")
    text_stroke_width = data.get("text_stroke_width")
    text_stroke_color = data.get("text_stroke_color")

    if not app_id:
        return jsonify({"error": "Missing app_id"}), 400

    set_setting("active_appid", str(app_id))

    if display_mode in {"obelisk", "ticker"}:
        set_setting("display_mode", display_mode)

    if text_color:
        set_setting("text_color", str(text_color))

    if text_stroke_width is not None:
        set_setting("text_stroke_width", str(text_stroke_width))

    if text_stroke_color:
        set_setting("text_stroke_color", str(text_stroke_color))

    state = AchievementService.refresh_game_achievements(app_id)

    return jsonify(state)

@app.route("/api/active-game", methods=["GET"])
def get_active_game():
    active_app_id = get_setting("active_appid")
    display_mode = get_setting("display_mode") or "obelisk"
    text_color = get_setting("text_color") or "#000000"
    text_stroke_width = get_setting("text_stroke_width") or "0"
    text_stroke_color = get_setting("text_stroke_color") or "#ffffff"

    if not active_app_id:
        return jsonify({
            "active_app_id": None,
            "display_mode": display_mode,
            "text_color": text_color,
            "text_stroke_width": text_stroke_width,
            "text_stroke_color": text_stroke_color,
            "game": None
        })

    game = get_game_by_app_id(str(active_app_id))

    return jsonify({
        "active_app_id": active_app_id,
        "display_mode": display_mode,
        "text_color": text_color,
        "text_stroke_width": text_stroke_width,
        "text_stroke_color": text_stroke_color,
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

@app.route("/api/test-toast", methods=["POST"])
def test_toast():
    data = request.get_json(silent=True) or {}

    fake_achievement = {
        "apiname": data.get("apiname", "TEST_TOAST"),
        "display_name": data.get("display_name", "Test Achievement"),
        "description": data.get("description", "This is a test toast."),
        "icon": data.get("icon", ""),
        "icon_gray": data.get("icon_gray", ""),
        "achieved": 1,
        "unlocktime": 0,
    }

    AchievementState.save_event({
        "latest": fake_achievement,
        "timestamp": int(time.time())
    })

    return jsonify({"ok": True, "latest": fake_achievement})