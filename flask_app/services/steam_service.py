import os
import requests

API_BASE = "https://api.steampowered.com/ISteamUserStats"
API_BASE_PLAYER = "https://api.steampowered.com/IPlayerService"


class SteamService:
    def __init__(self, api_key=None, steamid=None):
        self.api_key = api_key or os.getenv("STEAM_API_KEY")
        self.steamid = steamid or os.getenv("STEAM_STEAMID64")

        if not self.api_key:
            raise ValueError("Missing Steam API key.")
        if not self.steamid:
            raise ValueError("Missing SteamID64.")

    def get_schema_for_game(self, appid, language="english"):
        url = f"{API_BASE}/GetSchemaForGame/v2/"
        params = {
            "key": self.api_key,
            "appid": appid,
            "l": language,
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()

    def get_player_achievements(self, appid, language="english"):
        url = f"{API_BASE}/GetPlayerAchievements/v1/"
        params = {
            "key": self.api_key,
            "steamid": self.steamid,
            "appid": appid,
            "l": language,
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()

    def get_owned_games(self, include_appinfo=True):
        url = f"{API_BASE_PLAYER}/GetOwnedGames/v1/"
        params = {
            "key": self.api_key,
            "steamid": self.steamid,
            "include_appinfo": int(include_appinfo),
            "include_played_free_games": 1,
        }

        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()