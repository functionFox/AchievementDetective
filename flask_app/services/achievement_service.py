from flask_app.models.achievement_state import AchievementState
from flask_app.services.steam_service import SteamService


class AchievementService:
    @staticmethod
    def refresh_game_achievements(appid):
        steam = SteamService()
        state = steam.build_achievement_state(appid)
        AchievementState.save_state(state)
        return state