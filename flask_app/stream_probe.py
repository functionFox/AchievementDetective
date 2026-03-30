import os
import sys
import requests


API_BASE = "https://partner.steam-api.com/ISteamUserStats"


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_schema_for_game(api_key: str, appid: int, language: str = "english") -> dict:
    url = f"{API_BASE}/GetSchemaForGame/v2/"
    params = {
        "key": api_key,
        "appid": appid,
        "l": language,
    }
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def get_player_achievements(api_key: str, steamid: str, appid: int, language: str = "english") -> dict:
    url = f"{API_BASE}/GetPlayerAchievements/v1/"
    params = {
        "key": api_key,
        "steamid": steamid,
        "appid": appid,
        "l": language,
    }
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python steam_probe.py schema <appid>")
        print("  python steam_probe.py achievements <appid>")
        sys.exit(1)

    mode = sys.argv[1].lower()
    api_key = require_env("STEAM_API_KEY")
    appid = int(sys.argv[2])

    if mode == "schema":
        data = get_schema_for_game(api_key, appid)
        game = data.get("game", {})
        print(f"Game: {game.get('gameName', 'Unknown')}")
        achievements = game.get("availableGameStats", {}).get("achievements", [])
        print(f"Schema achievements found: {len(achievements)}")
        for ach in achievements[:5]:
            print(
                f"- api_name={ach.get('name')} | "
                f"display_name={ach.get('displayName')} | "
                f"hidden={ach.get('hidden')} | "
                f"icon={ach.get('icon')}"
            )

    elif mode == "achievements":
        steamid = require_env("STEAM_STEAMID64")
        data = get_player_achievements(api_key, steamid, appid)
        playerstats = data.get("playerstats", {})
        achievements = playerstats.get("achievements", [])
        unlocked = [a for a in achievements if a.get("achieved") == 1]
        print(f"Player achievement rows found: {len(achievements)}")
        print(f"Unlocked: {len(unlocked)}")
        for ach in unlocked[-5:]:
            print(
                f"- api_name={ach.get('apiname')} | "
                f"achieved={ach.get('achieved')} | "
                f"unlocktime={ach.get('unlocktime')}"
            )

    else:
        raise RuntimeError(f"Unknown mode: {mode}")


if __name__ == "__main__":
    main()