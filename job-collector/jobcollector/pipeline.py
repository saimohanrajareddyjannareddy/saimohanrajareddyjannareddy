from __future__ import annotations

import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from .location import is_remote, is_us
from .match import score_jobs
from .models import Job
from .sources import REGISTRY
from .sources.base import SourceError
from .visa import classify, norm_company

log = logging.getLogger("jobcollector")


def collect(cfg: dict, sources: list[str], since_hours: int, workers: int = 12) -> tuple[list[Job], dict]:
    queries = cfg.get("search_queries") or ["AI Engineer"]
    companies = cfg.get("companies") or {}
    tasks = []
    for name in sources:
        fn, kind = REGISTRY[name]
        if kind == "company":
            for slug in companies.get(name) or []:
                tasks.append((f"{name}:{slug}", fn, {"company": slug}))
        else:
            opts = dict((cfg.get("source_options") or {}).get(name) or {})
            opts.update(queries=queries, since_hours=since_hours)
            tasks.append((name, fn, opts))

    jobs: list[Job] = []
    stats: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = {pool.submit(fn, **kw): label for label, fn, kw in tasks}
        for fut in as_completed(futs):
            label = futs[fut]
            try:
                got = fut.result()
                jobs.extend(got)
                stats[label] = str(len(got))
            except SourceError as e:
                stats[label] = f"skipped ({e})"
                log.warning("%s: %s", label, e)
            except Exception as e:  # one broken source must not kill the run
                stats[label] = f"error ({type(e).__name__}: {e})"
                log.warning("%s failed: %s", label, e, exc_info=log.isEnabledFor(logging.DEBUG))
    return jobs, stats


def dedupe(jobs: list[Job]) -> list[Job]:
    """Same job from several sources: keep the copy with the longest description."""
    best: dict[str, Job] = {}
    for j in jobs:
        cur = best.get(j.key)
        if cur is None or len(j.description) > len(cur.description):
            if cur and not j.posted_at:
                j.posted_at = cur.posted_at
            best[j.key] = j
    return list(best.values())


def filter_and_rank(jobs: list[Job], resume_text: str, cfg: dict, *, since_hours: int,
                    sponsorship: str, sponsors: set[str], min_score: float,
                    remote_only: bool = False, include_undated: bool = False) -> list[Job]:
    f = cfg.get("filters") or {}
    now = datetime.now(timezone.utc)
    excl_title = [w.lower() for w in f.get("exclude_title_words") or []]
    excl_company = {norm_company(c) for c in f.get("exclude_companies") or []}
    require_title = [w.lower() for w in f.get("require_title_any") or []]

    kept = []
    for j in dedupe(jobs):
        if not j.title or not j.url:
            continue
        age = j.age_hours(now)
        if age is None and not include_undated:
            continue
        if age is not None and age > since_hours:
            continue
        t = j.title.lower()
        if any(re.search(rf"\b{re.escape(w)}\b", t) for w in excl_title):
            continue
        if require_title and not any(w in t for w in require_title):
            continue
        if norm_company(j.company) in excl_company:
            continue
        if f.get("us_only", True) and not is_us(j.location):
            continue
        if remote_only and not is_remote(j.location, j.remote):
            continue

        j.visa, j.visa_evidence = classify(j.description)
        j.known_sponsor = norm_company(j.company) in sponsors
        if sponsorship == "h1b" and j.visa == "no_sponsorship":
            continue
        if sponsorship == "strict" and not (j.visa == "sponsors" or (j.known_sponsor and j.visa != "no_sponsorship")):
            continue
        kept.append(j)

    score_jobs(kept, resume_text, cfg.get("profile") or {})
    kept = [j for j in kept if j.score >= min_score]
    kept.sort(key=lambda j: (j.score, j.visa == "sponsors", j.known_sponsor), reverse=True)
    return kept
