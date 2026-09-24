"""Scores how well a job lines up with your resume. 0-100, higher is better.

score = 45% skill overlap + 30% title fit + 25% resume/description text similarity,
minus penalties for experience requirements well above yours.
"""
from __future__ import annotations

import math
import re
from collections import Counter

from .models import Job
from .skills import extract_skills

_TOKEN = re.compile(r"[a-z][a-z0-9+#./-]{1,}")
_STOP = set("""a an and are as at be by for from has have in is it its of on or our that the this to we
will with you your they their them who what when where which while about into over more most such than
can all any each other some very also may must should would could not only own same so too just do does
work working team teams role roles experience years year strong ability skills using use used help new
including across within build building company job position candidate candidates join looking""".split())

_YEARS_RX = re.compile(r"(\d{1,2})\s*\+?\s*(?:-|to|–)?\s*(?:\d{1,2}\s*)?\+?\s*years?", re.I)


def tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN.findall(text.lower()) if t not in _STOP]


class TfIdf:
    def __init__(self, docs: list[list[str]]):
        self.n = len(docs) or 1
        df = Counter()
        for d in docs:
            df.update(set(d))
        self.idf = {t: math.log((1 + self.n) / (1 + c)) + 1 for t, c in df.items()}

    def vec(self, tokens: list[str]) -> dict[str, float]:
        tf = Counter(tokens)
        v = {t: (1 + math.log(c)) * self.idf.get(t, math.log(1 + self.n) + 1) for t, c in tf.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {t: x / norm for t, x in v.items()}


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(x * b.get(t, 0.0) for t, x in a.items())


def required_years(text: str) -> int | None:
    """Smallest 'N+ years' figure mentioned near the word experience."""
    found = []
    for m in _YEARS_RX.finditer(text):
        window = text[m.start(): m.end() + 60].lower()
        if "experience" in window or "exp" in window:
            n = int(m.group(1))
            if 0 < n <= 20:
                found.append(n)
    return min(found) if found else None


def title_fit(title: str, targets: list[str], related: list[str]) -> float:
    t = title.lower()
    if any(x.lower() in t for x in targets):
        return 1.0
    hits = sum(1 for x in related if re.search(rf"\b{re.escape(x.lower())}\b", t))
    return min(1.0, 0.35 * hits)


def score_jobs(jobs: list[Job], resume_text: str, profile: dict) -> None:
    resume_skills = extract_skills(resume_text) | set(profile.get("extra_skills") or [])
    targets = profile.get("target_titles") or []
    related = profile.get("related_title_words") or []
    my_years = float(profile.get("years_experience") or 0)
    senior_words = [w.lower() for w in profile.get("penalize_title_words") or []]
    core = set(profile.get("core_skills") or [])

    docs = [tokenize(j.title + " " + j.description) for j in jobs]
    tfidf = TfIdf(docs + [tokenize(resume_text)])
    rvec = tfidf.vec(tokenize(resume_text))

    for job, toks in zip(jobs, docs):
        job_skills = extract_skills(job.title + "\n" + job.description)
        matched = job_skills & resume_skills
        job.matched_skills = sorted(matched)
        job.missing_skills = sorted(job_skills - resume_skills)

        if job_skills:
            coverage = len(matched) / len(job_skills)
            depth = min(len(matched), 8) / 8
            core_bonus = 0.1 * min(len(matched & core), 3) / 3 if core else 0
            skill = min(1.0, 0.6 * coverage + 0.4 * depth + core_bonus)
        else:
            skill = 0.0
        title = title_fit(job.title, targets, related)
        sim = min(1.0, cosine(rvec, tfidf.vec(toks)) / 0.30)

        score = 100 * (0.45 * skill + 0.30 * title + 0.25 * sim)

        req = required_years(job.description)
        if req is not None and req > my_years + 1:
            score -= min(30, 7 * (req - my_years - 1))
        if any(re.search(rf"\b{re.escape(w)}\b", job.title.lower()) for w in senior_words):
            score -= 12
        job.score = round(max(0.0, min(100.0, score)), 1)
