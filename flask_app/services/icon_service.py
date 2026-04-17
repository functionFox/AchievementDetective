import hashlib
from pathlib import Path
from urllib.parse import urlparse

import requests

from flask_app.config.settings import ICON_DIR


class IconService:
    @staticmethod
    def cache_icon(app_id, icon_url):
        if not icon_url:
            return None

        icon_dir = Path(ICON_DIR) / str(app_id)
        icon_dir.mkdir(parents=True, exist_ok=True)

        parsed = urlparse(icon_url)
        suffix = Path(parsed.path).suffix or ".jpg"

        filename_seed = hashlib.sha1(icon_url.encode("utf-8")).hexdigest()
        filename = f"{filename_seed}{suffix}"

        file_path = icon_dir / filename

        if not file_path.exists():
            response = requests.get(icon_url, timeout=15)
            response.raise_for_status()
            file_path.write_bytes(response.content)

        return f"icons/{app_id}/{filename}"