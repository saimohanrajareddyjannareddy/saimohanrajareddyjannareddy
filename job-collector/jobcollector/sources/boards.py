"""Public job boards / aggregators that need no API key."""
from __future__ import annotations

import re
from datetime import datetime, timezone

from ..models import Job, html_to_text, parse_dt
from .base import get_json


def remotive(queries: list[str], **_) -> list[Job]:
    # Remotive asks clients to keep it to a few requests per day.
    jobs = []
    for q in queries[:4]:
        data = get_json("https://remotive.com/api/remote-jobs", params={"search": q, "limit": 200})
        for j in data.get("jobs", []):
            jobs.append(Job(
                source="remotive",
                title=j.get("title", ""),
                company=j.get("company_name", ""),
                url=j.get("url", ""),
                location=j.get("candidate_required_location", ""),
                description=html_to_text(j.get("description")),
                posted_at=parse_dt(j.get("publication_date")),
                remote=True,
                salary=j.get("salary", ""),
            ))
    return jobs


def remoteok(**_) -> list[Job]:
    data = get_json("https://remoteok.com/api")
    jobs = []
    for j in data:
        if not isinstance(j, dict) or "position" not in j:
            continue  # first element is a legal notice
        salary = ""
        if j.get("salary_min"):
            salary = f"${j['salary_min']:,}-${j.get('salary_max', 0):,}"
        jobs.append(Job(
            source="remoteok",
            title=j.get("position", ""),
            company=j.get("company", ""),
            url=j.get("url", ""),
            location=j.get("location", ""),
            description=html_to_text(j.get("description")) + "\n" + " ".join(j.get("tags") or []),
            posted_at=parse_dt(j.get("epoch") or j.get("date")),
            remote=True,
            salary=salary,
        ))
    return jobs


def themuse(queries: list[str], pages: int = 3, **_) -> list[Job]:
    jobs = []
    for cat in ("Software Engineering", "Data and Analytics", "Data Science"):
        for page in range(pages):
            data = get_json("https://www.themuse.com/api/public/jobs",
                            params={"category": cat, "page": page, "descending": "true"})
            for j in data.get("results", []):
                locs = ", ".join(l.get("name", "") for l in j.get("locations") or [])
                jobs.append(Job(
                    source="themuse",
                    title=j.get("name", ""),
                    company=(j.get("company") or {}).get("name", ""),
                    url=(j.get("refs") or {}).get("landing_page", ""),
                    location=locs,
                    description=html_to_text(j.get("contents")),
                    posted_at=parse_dt(j.get("publication_date")),
                    remote="remote" in locs.lower() or None,
                ))
            if page + 1 >= data.get("page_count", 0):
                break
    return jobs


def hackernews(**_) -> list[Job]:
    """Latest 'Ask HN: Who is hiring?' thread. Many posts state VISA explicitly."""
    hits = get_json("https://hn.algolia.com/api/v1/search_by_date",
                    params={"tags": "story,author_whoishiring", "hitsPerPage": 5}).get("hits", [])
    story = next((h for h in hits if "who is hiring" in h.get("title", "").lower()), None)
    if not story:
        return []
    item = get_json(f"https://hn.algolia.com/api/v1/items/{story['objectID']}")
    jobs = []
    for c in item.get("children") or []:
        text = html_to_text(c.get("text"))
        if not text:
            continue
        header = text.split("\n", 1)[0]
        # Convention: "Company | Role | Location | REMOTE | VISA | url"
        parts = [p.strip() for p in header.split("|")]
        company = parts[0][:80] if parts else "HN poster"
        title = parts[1][:120] if len(parts) > 1 else header[:120]
        location = next((p for p in parts[2:] if not re.match(r"https?://", p)), "")
        jobs.append(Job(
            source="hackernews",
            title=title,
            company=company,
            url=f"https://news.ycombinator.com/item?id={c.get('id')}",
            location=location,
            description=text,
            posted_at=parse_dt(c.get("created_at_i") or c.get("created_at")),
            remote="remote" in header.lower() or None,
        ))
    return jobs


def arbeitnow(**_) -> list[Job]:
    data = get_json("https://www.arbeitnow.com/api/job-board-api")
    jobs = []
    for j in data.get("data", []):
        jobs.append(Job(
            source="arbeitnow",
            title=j.get("title", ""),
            company=j.get("company_name", ""),
            url=j.get("url", ""),
            location=j.get("location", ""),
            description=html_to_text(j.get("description")) + "\n" + " ".join(j.get("tags") or []),
            posted_at=datetime.fromtimestamp(j["created_at"], tz=timezone.utc) if j.get("created_at") else None,
            remote=j.get("remote"),
        ))
    return jobs
