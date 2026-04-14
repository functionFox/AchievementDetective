from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable

class LibraryService:
    def find_steam_roots(self) -> list[Path]:
        """
        Return likely Steam root directories for Windows, Linux, and macOS.
        Only existing paths are returned.
        """
        candidates: list[Path] = []

        home = Path.home()

        # Env override first
        steam_dir = os.getenv("STEAM_DIR")
        if steam_dir:
            candidates.append(Path(steam_dir))

        # Linux
        candidates.append(home / ".local" / "share" / "Steam")
        candidates.append(home / ".steam" / "steam")

        # macOS
        candidates.append(home / "Library" / "Application Support" / "Steam")

        # Windows
        program_files_x86 = os.getenv("PROGRAMFILES(X86)")
        program_files = os.getenv("PROGRAMFILES")
        if program_files_x86:
            candidates.append(Path(program_files_x86) / "Steam")
        if program_files:
            candidates.append(Path(program_files) / "Steam")

        # De-dupe while preserving order
        seen: set[str] = set()
        valid: list[Path] = []

        for path in candidates:
            key = str(path).lower()
            if key in seen:
                continue
            seen.add(key)

            if path.exists() and path.is_dir():
                valid.append(path)

        return valid


    def find_libraryfolders_vdf(self, steam_roots: Iterable[Path]) -> Path | None:
        """
        Find the first valid steamapps/libraryfolders.vdf in the candidate roots.
        """
        for root in steam_roots:
            candidate = root / "steamapps" / "libraryfolders.vdf"
            if candidate.exists() and candidate.is_file():
                return candidate
        return None


    def parse_library_paths(self, libraryfolders_path: Path) -> list[Path]:
        """
        Parse libraryfolders.vdf and return all Steam library paths.

        This uses a light regex approach instead of a full VDF parser.
        Good enough for extracting 'path' entries from Steam's libraryfolders file.
        """
        text = libraryfolders_path.read_text(encoding="utf-8", errors="ignore")

        # Matches lines like: "path"    "D:\\SteamLibrary"
        raw_paths = re.findall(r'"path"\s*"([^"]+)"', text)

        libraries: list[Path] = []

        # Always include the main library that owns libraryfolders.vdf
        main_library = libraryfolders_path.parent.parent
        libraries.append(main_library)

        for raw in raw_paths:
            normalized = raw.replace("\\\\", "\\")
            path = Path(normalized)

            if path.exists() and path.is_dir():
                libraries.append(path)

        # De-dupe
        seen: set[str] = set()
        unique: list[Path] = []
        for path in libraries:
            key = str(path.resolve()).lower() if path.exists() else str(path).lower()
            if key in seen:
                continue
            seen.add(key)
            unique.append(path)

        return unique


    def parse_appmanifest(self, appmanifest_path: Path) -> dict[str, str] | None:
        """
        Parse a single appmanifest_*.acf file and extract app_id + name.
        """
        text = appmanifest_path.read_text(encoding="utf-8", errors="ignore")

        app_id_match = re.search(r'"appid"\s*"([^"]+)"', text)
        name_match = re.search(r'"name"\s*"([^"]+)"', text)

        if not app_id_match or not name_match:
            return None

        return {
            "app_id": app_id_match.group(1).strip(),
            "name": name_match.group(1).strip(),
        }


    def scan_installed_steam_games(self) -> list[dict[str, str]]:
        """
        Perform an initial Steam scan and return installed games.

        Returns:
            [
                {"app_id": "620", "name": "Portal 2"},
                ...
            ]
        """
        steam_roots = self.find_steam_roots()
        if not steam_roots:
            return []

        libraryfolders_path = self.find_libraryfolders_vdf(steam_roots)
        if libraryfolders_path is None:
            return []

        library_paths = self.parse_library_paths(libraryfolders_path)

        games: list[dict[str, str]] = []
        seen_app_ids: set[str] = set()

        for library_path in library_paths:
            steamapps_path = library_path / "steamapps"
            if not steamapps_path.exists():
                continue

            for manifest_path in steamapps_path.glob("appmanifest_*.acf"):
                game = self.parse_appmanifest(manifest_path)
                if game is None:
                    continue

                app_id = game["app_id"]
                if app_id in seen_app_ids:
                    continue

                seen_app_ids.add(app_id)
                games.append(game)

        games.sort(key=lambda g: g["name"].lower())
        return games