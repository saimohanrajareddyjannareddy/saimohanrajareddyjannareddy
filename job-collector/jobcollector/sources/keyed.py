"""Sources that need a (free-tier) API key or an optional package.

These are how you get LinkedIn / Indeed / Glassdoor / ZipRecruiter coverage.
Those sites have no public API and forbid scraping in their terms, so the
options are a licensed aggregator (JSearch, Adzuna) or the JobSpy scraper at
your own risk.
"""
from __future__ import annotations

import logging
import os

from ..models import Job, parse_dt
from .base import SourceError, get_json

log = logging.getLogger("jobcollector")


def jsearch(queries: list[str], since_hours: int, location: str = "United States", **_) -> list[Job]:
    """RapidAPI JSearch: Google-for-Jobs index (LinkedIn, Indeed, Glassdoor, company sites).
    Free tier is ~200 requests/month; each query here costs 1 request per page."""
    key = os.environ.get("JSEARCH_API_KEY")
    if not key:
        raise SourceError("set JSEARCH_API_KEY (free at rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch)")
    date_posted = "today" if since_hours <= 24 else "3days" if since_hours <= 72 else "week" if since_hours <= 168 else "month"
    jobs = []
    for q in queries:
        data = get_json("https://jsearch.p.rapidapi.com/search",
                        params={"query": f"{q} in {location}", "page": 1, "num_pages": 2,
                                "date_posted": date_posted, "country": "us"},
                        headers={"X-RapidAPI-Key": key, "X-RapidAPI-Host": "jsearch.p.rapidapi.com"})
        for j in data.get("data", []):
            loc = ", ".join(x for x in (j.get("job_city"), j.get("job_state"), j.get("job_country")) if x)
            jobs.append(Job(
                source=f"jsearch:{(j.get('job_publisher') or '').lower()}",
                title=j.get("job_title", ""),
                company=j.get("employer_name", ""),
                url=j.get("job_apply_link", ""),
                location=loc,
                description=j.get("job_description", ""),
                posted_at=parse_dt(j.get("job_posted_at_timestamp") or j.get("job_posted_at_datetime_utc")),
                remote=j.get("job_is_remote"),
            ))
    return jobs


def adzuna(queries: list[str], since_hours: int, **_) -> list[Job]:
    """Adzuna US index. Free key at developer.adzuna.com. Descriptions are
    truncated snippets, so skill matching is weaker for these."""
    app_id, app_key = os.environ.get("ADZUNA_APP_ID"), os.environ.get("ADZUNA_APP_KEY")
    if not (app_id and app_key):
        raise SourceError("set ADZUNA_APP_ID and ADZUNA_APP_KEY")
    days = max(1, round(since_hours / 24))
    jobs = []
    for q in queries:
        for page in (1, 2):
            data = get_json(f"https://api.adzuna.com/v1/api/jobs/us/search/{page}",
                            params={"app_id": app_id, "app_key": app_key, "what": q,
                                    "max_days_old": days, "results_per_page": 50,
                                    "sort_by": "date", "content-type": "application/json"})
            for j in data.get("results", []):
                sal = ""
                if j.get("salary_min"):
                    sal = f"${int(j['salary_min']):,}-${int(j.get('salary_max') or 0):,}"
                jobs.append(Job(
                    source="adzuna",
                    title=j.get("title", ""),
                    company=(j.get("company") or {}).get("display_name", ""),
                    url=j.get("redirect_url", ""),
                    location=(j.get("location") or {}).get("display_name", ""),
                    description=j.get("description", ""),
                    posted_at=parse_dt(j.get("created")),
                    salary=sal,
                ))
    return jobs


def jobspy(queries: list[str], since_hours: int, location: str = "United States",
           sites=("indeed", "linkedin", "glassdoor", "zip_recruiter", "google"), results: int = 50, **_) -> list[Job]:
    """Scrapes LinkedIn/Indeed/Glassdoor/ZipRecruiter via python-jobspy.
    This violates those sites' ToS and LinkedIn rate-limits/blocks aggressively.
    Off by default; enable only if you accept that risk."""
    try:
        from jobspy import scrape_jobs
    except ImportError as e:
        raise SourceError("pip install python-jobspy") from e
    jobs = []
    for q in queries:
        df = scrape_jobs(site_name=list(sites), search_term=q, location=location,
                         results_wanted=results, hours_old=since_hours, country_indeed="USA",
                         linkedin_fetch_description=True)
        for row in df.to_dict("records"):
            def s(k):
                v = row.get(k)
                return "" if v is None or v != v else str(v)  # v != v catches NaN
            jobs.append(Job(
                source=f"jobspy:{s('site')}",
                title=s("title"),
                company=s("company"),
                url=s("job_url"),
                location=s("location"),
                description=s("description"),
                posted_at=parse_dt(s("date_posted")),
                remote=bool(row.get("is_remote")) if row.get("is_remote") is not None else None,
            ))
    return jobs
