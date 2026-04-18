# Achievement Detective

Achievement Detective is a local Flask-based OBS browser-source overlay for Steam achievements.

It polls Steam achievement data for a selected game, displays achievement progress in an overlay, and shows an animated toast when a new achievement unlock is detected.

## Current features

- Steam owned-game scan through the Steam Web API
- Local game selection/config page
- Cached achievement data in SQLite
- Cached achievement icons under `flask_app/static/icons/`
- OBS browser-source overlay at `/`
- Config page at `/config`
- Display modes:
  - ticker
  - obelisk
- Configurable overlay text color/stroke
- Configurable ticker bar color/opacity
- Animated achievement unlock toast with icon, title, and description
- Test toast endpoint for layout/debugging

## Project status

This project is currently in active development. It is functional enough for local testing, but setup and configuration are still developer-oriented.

Planned/future ideas include:

- Toast position options
- Toast animation presets
- Notification sounds
- External event broadcasting for integrations such as Streamer.bot or OBS workflows
- Optional clip-trigger workflows handled outside Achievement Detective

## Requirements

- Python 3
- Flask
- python-dotenv
- requests
- A Steam Web API key
- Your SteamID64
- OBS Studio with a Browser Source

Until a dedicated dependency file is added, install the Python dependencies manually:

```bash
python -m pip install flask python-dotenv requests
```

## Environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=replace-this-with-any-local-dev-secret
STEAM_API_KEY=your-steam-web-api-key
STEAM_STEAMID64=your-steamid64
```

`SECRET_KEY` is used by Flask. `STEAM_API_KEY` and `STEAM_STEAMID64` are required for Steam API calls.

## First-time database setup

Initialize the local SQLite database:

```bash
python -c "from flask_app.services.db_service import init_db; init_db()"
```

This creates `achievement_detective.db` in the project root.

## Running the app

Start the Flask server:

```bash
python server.py
```

By default, the app runs at:

```text
http://127.0.0.1:5000/
```

The config page should open automatically. If it does not, open:

```text
http://127.0.0.1:5000/config
```

## OBS setup

Add a Browser Source in OBS with this URL:

```text
http://127.0.0.1:5000/
```

Recommended starting size:

```text
Width: 1920
Height: 1080
```

The ticker is designed to sit along the bottom of the scene, while achievement toasts appear above it.

## Basic usage

1. Start the Flask server.
2. Open the config page.
3. Select a Steam game.
4. Choose a display mode.
5. Apply settings.
6. Add or refresh the OBS Browser Source.
7. Play the selected game and unlock an achievement.

Achievement Detective compares the previous cached achievement state against the latest Steam state. When it detects a newly unlocked achievement, it saves a latest-unlock event for the overlay to display.

## Testing the toast

You can trigger a fake toast with curl:

```bash
curl -X POST http://127.0.0.1:5000/api/test-toast \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "1000K",
    "description": "Attain a score of 1,000,000 in one hand.",
    "icon": "icons/2379780/0ca3a30f4ba812b33ce85fc82b6d4ecc9f567df9.jpg"
  }'
```

The icon path should be relative to `flask_app/static/`.

## Main routes

```text
GET  /                         Overlay page
GET  /config                   Config page
GET  /api/health               Health check
GET  /api/games                List cached/scanned games
POST /api/select-game          Save active game and overlay settings
GET  /api/active-game          Return active game/settings
GET  /api/achievements         Return achievement state
POST /api/refresh-achievements Refresh achievements for active/selected game
GET  /api/state                Return current overlay state
GET  /api/event                Return latest achievement event
POST /api/test-toast           Trigger a fake toast event
```

## Notes

Achievement Detective does not currently handle Twitch authentication or clip creation directly. The preferred future approach is for Achievement Detective to emit a local event when an achievement unlocks, allowing external tools such as Streamer.bot, OBS scripts, or Stream Deck workflows to handle Twitch-specific actions.
