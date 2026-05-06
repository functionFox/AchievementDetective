import json
import os
from flask_app.config.settings import DATA_DIR, STATE_FILE, EVENT_FILE

class AchievementState:
    @staticmethod
    def ensure_files():
        os.makedirs(DATA_DIR, exist_ok=True)

        if not os.path.exists(STATE_FILE):
            with open(STATE_FILE, "w", encoding="utf-8") as file:
                json.dump({
                    "achievements": [],
                    "unlocked": 0,
                    "total": 0
                }, file, indent=2)

        if not os.path.exists(EVENT_FILE):
            with open(EVENT_FILE, "w", encoding="utf-8") as file:
                json.dump({
                    "events": []
                }, file, indent=2)

    @staticmethod
    def _load_json(path, default):
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def _save_json(path, data):
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    @classmethod
    def load_state(cls):
        cls.ensure_files()
        return cls._load_json(STATE_FILE, {
            "achievements": [],
            "unlocked": 0,
            "total": 0
        })

    @classmethod
    def save_state(cls, data):
        cls.ensure_files()
        cls._save_json(STATE_FILE, data)

    @classmethod
    def load_event(cls):
        cls.ensure_files()
        data = cls._load_json(EVENT_FILE, {
            "events": []
        })

        if "events" not in data:
            data = {
                "events": [data] if data.get("latest") else []
            }

        return data

    @classmethod
    def save_event(cls, data):
        cls.ensure_files()
        event_data = cls.load_event()
        events = event_data.get("events", [])

        if data.get("latest"):
            events.append(data)

        cls._save_json(EVENT_FILE, {
            "events": events[-20:]
        })

    @classmethod
    def pop_next_event_for_appid(cls, appid):
        cls.ensure_files()
        event_data = cls.load_event()
        events = event_data.get("events", [])

        for index, event in enumerate(events):
            if str(event.get("appid")) == str(appid):
                next_event = events.pop(index)
                cls._save_json(EVENT_FILE, {
                    "events": events[-20:]
                })
                return next_event

        return {}