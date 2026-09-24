from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from jobcollector import cli
from jobcollector.location import is_us
from jobcollector.match import required_years, score_jobs
from jobcollector.models import Job, html_to_text, parse_dt
from jobcollector.pipeline import filter_and_rank
from jobcollector.skills import extract_skills
from jobcollector.sources import ats, boards
from jobcollector.visa import classify, load_sponsors, norm_company

ROOT = Path(__file__).resolve().parent.parent
NOW = datetime.now(timezone.utc)
iso = lambda hours: (NOW - timedelta(hours=hours)).isoformat()
RESUME = (ROOT / "sample_profile.md").read_text()

AI_DESC = ("We are hiring an AI Engineer to build LLM agents and RAG pipelines in Python. "
           "You will work with OpenAI and Anthropic APIs, Pinecone, embeddings, PostgreSQL, Docker and AWS. "
           "2+ years of experience building production systems. We sponsor H-1B visas.")


# ---------- visa ----------

@pytest.mark.parametrize("text,expected", [
    ("We are unable to sponsor visas for this role.", "no_sponsorship"),
    ("This position does not offer visa sponsorship.", "no_sponsorship"),
    ("Candidates must be authorized to work in the US without the need for current or future sponsorship.", "no_sponsorship"),
    ("Must be a U.S. citizen due to ITAR.", "no_sponsorship"),
    ("Active Secret clearance required.", "no_sponsorship"),
    ("Visa sponsorship is available for this position.", "sponsors"),
    ("We sponsor H-1B visas and support transfers.", "sponsors"),
    ("We offer immigration support for qualified candidates.", "sponsors"),
    ("Great benefits, 401k, and free lunch.", "unknown"),
])
def test_visa_classify(text, expected):
    assert classify(text)[0] == expected


def test_visa_hn_header():
    assert classify("Acme | ML Engineer | SF | ONSITE | VISA | https://acme.com\nWe build things.")[0] == "sponsors"


def test_sponsor_list_normalization(tmp_path):
    p = tmp_path / "s.txt"
    p.write_text("Scale AI\nStripe, Inc.\n# comment\n")
    s = load_sponsors([p])
    assert norm_company("Scale") in s and norm_company("Stripe") in s


def test_uscis_csv(tmp_path):
    p = tmp_path / "uscis.csv"
    p.write_text('Fiscal Year,Employer (Petitioner) Name,Initial Approval,Continuing Approval\n'
                 '2025,ACME ROBOTICS INC,3,1\n2025,TINY SHOP LLC,0,0\n')
    s = load_sponsors([p])
    assert "acmerobotics" in s and "tinyshop" not in s


# ---------- parsing helpers ----------

def test_parse_dt_formats():
    assert parse_dt(1700000000000).year == 2023
    assert parse_dt(1700000000).year == 2023
    assert parse_dt("2026-09-23T10:00:00Z").tzinfo is not None
    assert parse_dt("2026-09-23").day == 23
    assert parse_dt("garbage") is None


def test_html_to_text_greenhouse_double_escape():
    assert "Python" in html_to_text("&lt;p&gt;Python &amp;amp; SQL&lt;/p&gt;")
    assert "<" not in html_to_text("&lt;p&gt;x&lt;/p&gt;")


@pytest.mark.parametrize("loc,us", [
    ("San Francisco, CA", True), ("Remote - US", True), ("New York, NY; London, UK", True),
    ("London, UK", False), ("Bengaluru, India", False), ("Remote", True), ("Toronto, Canada", False),
    ("St. Louis, MO", True), ("", True),
])
def test_is_us(loc, us):
    assert is_us(loc) is us


def test_required_years():
    assert required_years("Requires 5+ years of experience in Python") == 5
    assert required_years("3-5 years experience") == 3
    assert required_years("Founded 10 years ago") is None


def test_resume_skills():
    s = extract_skills(RESUME)
    for k in ("Python", "RAG", "Pinecone", "Playwright", "n8n", "PostgreSQL", "AI Agents"):
        assert k in s


# ---------- source adapters (fixtures in each API's shape) ----------

def test_greenhouse(monkeypatch):
    monkeypatch.setattr(ats, "get_json", lambda url, **kw: {"jobs": [{
        "title": "AI Engineer", "absolute_url": "https://x/1", "location": {"name": "Remote - US"},
        "content": "&lt;p&gt;Python LLM&lt;/p&gt;", "updated_at": iso(1), "first_published": iso(5),
        "company_name": "Acme"}]})
    [j] = ats.greenhouse("acme")
    assert j.company == "Acme" and "Python" in j.description and 4.5 < j.age_hours() < 5.5


def test_lever(monkeypatch):
    ms = int((NOW - timedelta(hours=3)).timestamp() * 1000)
    monkeypatch.setattr(ats, "get_json", lambda url, **kw: [{
        "text": "ML Engineer", "hostedUrl": "https://x/2", "createdAt": ms, "descriptionPlain": "Build RAG",
        "categories": {"location": "Seattle, WA"}, "lists": [{"text": "Requirements", "content": "<li>PyTorch</li>"}],
        "workplaceType": "hybrid"}])
    [j] = ats.lever("acme")
    assert "PyTorch" in j.description and j.location == "Seattle, WA" and 2.5 < j.age_hours() < 3.5


def test_ashby(monkeypatch):
    monkeypatch.setattr(ats, "get_json", lambda url, **kw: {"jobs": [
        {"title": "LLM Engineer", "jobUrl": "https://x/3", "location": "NYC", "descriptionPlain": "agents",
         "publishedAt": iso(2), "isRemote": False, "isListed": True,
         "compensation": {"compensationTierSummary": "$150K – $200K"}},
        {"title": "Hidden", "jobUrl": "https://x/4", "isListed": False}]})
    jobs = ats.ashby("acme")
    assert len(jobs) == 1 and jobs[0].salary.startswith("$150K")


def test_remoteok_skips_legal_notice(monkeypatch):
    monkeypatch.setattr(boards, "get_json", lambda url, **kw: [
        {"legal": "notice"},
        {"position": "AI Engineer", "company": "R", "url": "https://x/5", "epoch": int(NOW.timestamp()) - 3600,
         "description": "LLM", "tags": ["python"], "location": "Worldwide"}])
    [j] = boards.remoteok()
    assert j.remote and "python" in j.description


def test_hackernews(monkeypatch):
    def fake(url, **kw):
        if "search_by_date" in url:
            return {"hits": [{"title": "Ask HN: Who is hiring? (September 2026)", "objectID": "99"}]}
        return {"children": [{"id": 1, "created_at_i": int(NOW.timestamp()) - 7200,
                               "text": "Acme | AI Engineer | Austin, TX | ONSITE | VISA<p>Python, LLMs, RAG."}]}
    monkeypatch.setattr(boards, "get_json", fake)
    [j] = boards.hackernews()
    assert j.company == "Acme" and j.title == "AI Engineer" and j.location == "Austin, TX"
    assert classify(j.description)[0] == "sponsors"


# ---------- ranking ----------

def _job(title, desc, hours=2, loc="Remote - US", company="Acme"):
    return Job(source="t", title=title, company=company, url=f"https://x/{title}", location=loc,
               description=desc, posted_at=NOW - timedelta(hours=hours))


def test_ranking_prefers_aligned_role():
    cfg = {"profile": {"years_experience": 2, "target_titles": ["AI Engineer"], "related_title_words": ["ai", "ml"],
                       "penalize_title_words": ["senior"]},
           "filters": {"exclude_title_words": ["director"]}}
    jobs = [
        _job("AI Engineer", AI_DESC),
        _job("Senior AI Engineer", AI_DESC.replace("2+ years", "8+ years")),
        _job("Accountant", "Excel, GAAP, month-end close. 3 years experience."),
        _job("Director of AI", AI_DESC),
        _job("AI Engineer (old)", AI_DESC, hours=200),
        _job("ML Engineer London", AI_DESC, loc="London, UK"),
        _job("AI Engineer - Cleared", AI_DESC.replace("We sponsor H-1B visas.", "Must be a US citizen."), company="Def"),
    ]
    out = filter_and_rank(jobs, RESUME, cfg, since_hours=24, sponsorship="h1b", sponsors=set(), min_score=0)
    titles = [j.title for j in out]
    assert titles[0] == "AI Engineer"
    assert "Director of AI" not in titles and "AI Engineer (old)" not in titles
    assert "ML Engineer London" not in titles and "AI Engineer - Cleared" not in titles
    assert titles.index("Senior AI Engineer") < titles.index("Accountant")
    assert out[0].visa == "sponsors" and "RAG" in out[0].matched_skills


def test_strict_mode_uses_known_sponsors():
    plain = AI_DESC.replace("We sponsor H-1B visas.", "")
    jobs = [_job("AI Engineer", plain, company="Stripe"), _job("AI Engineer 2", plain, company="Nobody Co")]
    out = filter_and_rank(jobs, RESUME, {"profile": {}}, since_hours=24, sponsorship="strict",
                          sponsors={norm_company("Stripe")}, min_score=0)
    assert [j.company for j in out] == ["Stripe"]


def test_dedupe_across_sources():
    a = _job("AI Engineer", "short")
    b = _job("AI Engineer", AI_DESC)
    out = filter_and_rank([a, b], RESUME, {"profile": {}}, since_hours=24, sponsorship="any", sponsors=set(), min_score=0)
    assert len(out) == 1 and out[0].description == AI_DESC


# ---------- end to end through the CLI ----------

def test_cli_end_to_end(monkeypatch, tmp_path, capsys):
    from jobcollector import sources
    fake = lambda **kw: [_job("AI Engineer", AI_DESC, company="Anthropic"), _job("Chef", "Cook food.")]
    monkeypatch.setitem(sources.REGISTRY, "remoteok", (fake, "search"))
    cfg = tmp_path / "config.yaml"
    cfg.write_text((ROOT / "config.yaml").read_text().replace("resume_path: sample_profile.md",
                                                             f"resume_path: {ROOT / 'sample_profile.md'}"))
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "h1b_sponsors.txt").write_text("Anthropic\n")
    rc = cli.main(["run", "--config", str(cfg), "--sources", "remoteok", "--since", "1d", "--out", str(tmp_path / "r")])
    assert rc == 0
    out = capsys.readouterr().out
    assert "AI Engineer — Anthropic" in out and "Chef" not in out
    assert (tmp_path / "r" / "latest.html").read_text().count("<tr data-visa") == 1
    # second run: same job is no longer new
    cli.main(["run", "--config", str(cfg), "--sources", "remoteok", "--out", str(tmp_path / "r")])
    assert "NEW" not in capsys.readouterr().out.split("title — company")[1]


def test_visa_ignores_non_visa_sponsoring():
    assert classify("We sponsor local hackathons and happy to sponsor conference travel.")[0] == "unknown"
