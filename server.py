from threading import Timer
import webbrowser

from flask_app import app
from flask_app.controllers import overlay_controller, api_controller


def open_config_page():
    webbrowser.open("http://127.0.0.1:5000/config")


if __name__ == "__main__":
    Timer(1.0, open_config_page).start()
    app.run(debug=True)