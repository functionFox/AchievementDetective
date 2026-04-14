from __future__ import annotations

import sqlite3
import time
from pathlib import Path

DB_PATH = Path("achievement_detective.db")


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)

def init_db() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                app_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL,
                last_seen INTEGER NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL
            )
        """)

        conn.commit()

def upsert_games(games: list[dict[str, str]]) -> None:
    now = int(time.time())

    with get_connection() as conn:
        cursor = conn.cursor()

        for game in games:
            cursor.execute("""
                INSERT INTO games (app_id, name, created_at, updated_at, last_seen)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(app_id) DO UPDATE SET
                    name = excluded.name,
                    updated_at = excluded.updated_at,
                    last_seen = excluded.last_seen
            """, (
                game["app_id"],
                game["name"],
                now,
                now,
                now,
            ))

        conn.commit()

def get_games() -> list[dict[str, str]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT app_id, name, created_at, updated_at, last_seen
            FROM games
            ORDER BY name COLLATE NOCASE
        """)

        rows = cursor.fetchall()

    return [
        {
            "app_id": row[0],
            "name": row[1],
            "created_at": row[2],
            "updated_at": row[3],
            "last_seen": row[4],
        }
        for row in rows
    ]

def set_setting(key: str, value: str) -> None:
    now = int(time.time())

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO settings (key, value, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at
        """, (key, value, now, now))
        conn.commit()


def get_setting(key: str) -> str | None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT value
            FROM settings
            WHERE key = ?
        """, (key,))
        row = cursor.fetchone()

    return row[0] if row else None

def get_game_by_app_id(app_id: str) -> dict[str, str | int] | None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT app_id, name, created_at, updated_at, last_seen
            FROM games
            WHERE app_id = ?
        """, (app_id,))
        row = cursor.fetchone()

    if row is None:
        return None

    return {
        "app_id": row[0],
        "name": row[1],
        "created_at": row[2],
        "updated_at": row[3],
        "last_seen": row[4],
    }