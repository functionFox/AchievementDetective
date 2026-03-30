import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
STATE_FILE = os.path.join(DATA_DIR, "state.json")
EVENT_FILE = os.path.join(DATA_DIR, "event.json")
ICON_DIR = os.path.join(BASE_DIR, "flask_app", "static", "icons")