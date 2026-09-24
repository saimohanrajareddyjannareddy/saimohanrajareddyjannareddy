"""Company career boards hosted on Greenhouse, Lever and Ashby.

These are public JSON endpoints the ATS vendors provide for embedding job
boards, so they are the most reliable and ToS-friendly way to get complete,
fresh postings straight from employers. You choose which companies to poll
in config.yaml.
"""
from __future__ import annotations

from ..models import Job, html_to_text, parse_dt
from .base import get_json


def greenhouse(company: str) -> list[Job]:
    data = get_json(f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs",
                    params={"content": "true"})
    jobs = []
    for j in data.get("jobs", []):
        jobs.append(Job(
            source="greenhouse",
            title=j.get("title", ""),
            company=j.get("company_name") or company,
            url=j.get("absolute_url", ""),
            location=(j.get("location") or {}).get("name", ""),
            description=html_to_text(j.get("content")),
            # first_published is the real post date; updated_at changes on edits.
            posted_at=parse_dt(j.get("first_published") or j.get("updated_at")),
        ))
    return jobs


def lever(company: str) -> list[Job]:
    data = get_json(f"https://api.lever.co/v0/postings/{company}", params={"mode": "json"})
    jobs = []
    for j in data:
        cats = j.get("categories") or {}
        parts = [j.get("descriptionPlain", "")]
        for lst in j.get("lists") or []:
            parts.append(lst.get("text", ""))
            parts.append(html_to_text(lst.get("content")))
        parts.append(j.get("additionalPlain", ""))
        jobs.append(Job(
            source="lever",
            title=j.get("text", ""),
            company=company,
            url=j.get("hostedUrl", ""),
            location=cats.get("location") or ", ".join(cats.get("allLocations") or []),
            description="\n".join(p for p in parts if p),
            posted_at=parse_dt(j.get("createdAt")),
            remote=(j.get("workplaceType") == "remote") or None,
        ))
    return jobs


def ashby(company: str) -> list[Job]:
    data = get_json(f"https://api.ashbyhq.com/posting-api/job-board/{company}",
                    params={"includeCompensation": "true"})
    jobs = []
    for j in data.get("jobs", []):
        if j.get("isListed") is False:
            continue
        comp = (j.get("compensation") or {}).get("compensationTierSummary") or ""
        jobs.append(Job(
            source="ashby",
            title=j.get("title", ""),
            company=company,
            url=j.get("jobUrl") or j.get("applyUrl", ""),
            location=j.get("location", ""),
            description=j.get("descriptionPlain") or html_to_text(j.get("descriptionHtml")),
            posted_at=parse_dt(j.get("publishedAt")),
            remote=j.get("isRemote"),
            salary=comp,
        ))
    return jobs
