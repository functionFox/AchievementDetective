from threading import Timer
import webbrowser

from flask_app import app
from flask_app.controllers import overlay_controller, api_controller
from flask_app.services.db_service import init_db

from flask_app.services.library_service import scan_steam_games
from flask_app.services.db_service import init_db, sync_installed_games

def open_config_page():
    webbrowser.open("http://127.0.0.1:5000/config")


if __name__ == "__main__":
    init_db()
    sync_installed_games(scan_steam_games())
    # Timer(1.0, open_config_page).start()
    app.run(debug=True)