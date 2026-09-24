from __future__ import annotations

import hashlib
import html
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Job:
    source: str
    title: str
    company: str
    url: str
    location: str = ""
    description: str = ""
    posted_at: datetime | None = None
    remote: bool | None = None
    salary: str = ""
    # Filled in by the pipeline
    score: float = 0.0
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    visa: str = "unknown"          # sponsors | no_sponsorship | unknown
    visa_evidence: str = ""
    known_sponsor: bool = False
    is_new: bool = True

    @property
    def key(self) -> str:
        """Stable identity used for dedupe across sources and runs."""
        norm = lambda s: re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()
        raw = f"{norm(self.company)}|{norm(self.title)}|{norm(self.location)}"
        return hashlib.sha1(raw.encode()).hexdigest()[:16]

    def age_hours(self, now: datetime | None = None) -> float | None:
        if not self.posted_at:
            return None
        now = now or datetime.now(timezone.utc)
        return (now - self.posted_at).total_seconds() / 3600


_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"[ \t\r\f\v]+")


def html_to_text(s: str | None) -> str:
    if not s:
        return ""
    # Greenhouse double-escapes its HTML, so unescape before stripping tags.
    s = html.unescape(html.unescape(s))
    s = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</h\d>", "\n", s)
    s = _TAG_RE.sub(" ", s)
    s = _WS_RE.sub(" ", s)
    return re.sub(r"\n\s*\n+", "\n", s).strip()


def parse_dt(value) -> datetime | None:
    """Accepts ISO strings, epoch seconds, or epoch milliseconds."""
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        ts = value / 1000 if value > 1e11 else value
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    s = str(value).strip()
    if s.isdigit():
        return parse_dt(int(s))
    s = s.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
