"""Remembers jobs across runs so each report can flag what's new."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .models import Job


class Store:
    def __init__(self, path: str | Path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path))
        self.db.execute("""CREATE TABLE IF NOT EXISTS seen (
            key TEXT PRIMARY KEY, first_seen TEXT, title TEXT, company TEXT, url TEXT,
            score REAL, status TEXT DEFAULT '')""")

    def mark(self, jobs: list[Job]) -> None:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        cur = self.db.cursor()
        for j in jobs:
            row = cur.execute("SELECT 1 FROM seen WHERE key=?", (j.key,)).fetchone()
            j.is_new = row is None
            if j.is_new:
                cur.execute("INSERT INTO seen(key, first_seen, title, company, url, score) VALUES (?,?,?,?,?,?)",
                            (j.key, now, j.title, j.company, j.url, j.score))
            else:
                cur.execute("UPDATE seen SET score=? WHERE key=?", (j.score, j.key))
        self.db.commit()
