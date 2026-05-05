import time

from flask_app.models.achievement_state import AchievementState
from flask_app.services.icon_service import IconService
from flask_app.services.steam_service import SteamService
from flask_app.services.db_service import (
    upsert_achievements,
    get_achievement_state_by_app_id,
    mark_achievement_toasted
)

class AchievementService:
    @staticmethod
    def refresh_game_achievements(appid):
        old_state = get_achievement_state_by_app_id(str(appid))

        steam = SteamService()
        state = steam.build_achievement_state(appid)

        for achievement in state["achievements"]:
            achievement["icon"] = IconService.cache_icon(appid, achievement.get("icon"))
            achievement["icon_gray"] = IconService.cache_icon(appid, achievement.get("icon_gray"))

        upsert_achievements(str(appid), state["achievements"])
        AchievementState.save_state(state)

        if old_state is not None:
            old_lookup = {
                achievement["apiname"]: achievement
                for achievement in old_state["achievements"]
            }

            newly_unlocked = [
                achievement
                for achievement in state["achievements"]
                if achievement["achieved"]
                and not old_lookup.get(achievement["apiname"], {}).get("toasted", 0)
            ]

            if newly_unlocked:
                AchievementState.save_event({
                    "latest": newly_unlocked[-1],
                    "timestamp": int(time.time())
                })

            mark_achievement_toasted(str(appid), newly_unlocked[-1]["apiname"])

        return state