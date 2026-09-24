# Job Collector

Pulls fresh postings (last 24h, 3 days, a week, anything) from many sources, drops the ones that
say no sponsorship or US-citizens-only, and ranks the rest against your resume.

```
python -m jobcollector --resume resumes/my_resume.pdf --since 24h --sponsorship h1b
```

Output: a sortable/filterable HTML report and a CSV in `reports/`, plus a top-25 in the terminal.
Jobs you've already seen in a previous run are not flagged `NEW`.

## Setup

```bash
cd job-collector
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
mkdir -p resumes && cp ~/Downloads/resume.pdf resumes/   # resumes/ is gitignored
python -m jobcollector skills --resume resumes/resume.pdf  # check which skills it read
python -m jobcollector --resume resumes/resume.pdf --since 1w
```

`config.yaml` holds your target titles, years of experience, filters, search queries and the
company list. The defaults were set from the GitHub profile README (AI/LLM engineer, ~2 yrs).

## Options

| flag | meaning |
|---|---|
| `--since 24h` / `3d` / `1w` | only postings this recent (default 24h) |
| `--sponsorship h1b` | default. drops postings that say no sponsorship, citizens only, clearance, ITAR |
| `--sponsorship strict` | only postings that say they sponsor, or employers on your H-1B list that don't say no |
| `--sponsorship any` | no visa filtering |
| `--remote` | remote only |
| `--min-score 50` | tighten the match threshold (default 35) |
| `--sources greenhouse,ashby,jsearch` | pick sources (`python -m jobcollector sources` lists them) |
| `--include-undated` | keep postings with no date |

## Sources

| source | what it covers | key needed |
|---|---|---|
| `greenhouse`, `lever`, `ashby` | career boards of ~70 companies listed in `config.yaml` (Anthropic, OpenAI, Databricks, Stripe, Scale, Cohere, Ramp, …). Full descriptions, exact post dates. Add any company by its board slug. | no |
| `remotive`, `remoteok` | remote tech jobs | no |
| `themuse` | general US tech jobs | no |
| `hackernews` | latest "Who is hiring?" thread. Posters often write VISA explicitly | no |
| `arbeitnow` | mostly Europe; off by default | no |
| `jsearch` | Google-for-Jobs index: **LinkedIn, Indeed, Glassdoor, ZipRecruiter**, company sites. Best single add. ~200 free requests/month on RapidAPI | `JSEARCH_API_KEY` |
| `adzuna` | large US aggregator (descriptions are snippets) | `ADZUNA_APP_ID`, `ADZUNA_APP_KEY` |
| `jobspy` | scrapes LinkedIn/Indeed/Glassdoor/ZipRecruiter directly via `python-jobspy` | none, but see below |

"Every posting from every source" isn't possible. LinkedIn and Indeed have no public API and forbid
scraping. JSearch is the licensed way to get their listings. `jobspy` scrapes them anyway; it works
today, but it breaks their terms and LinkedIn will rate-limit or block you. It's opt-in for that reason.

## How sponsorship is judged

1. **Posting text.** Regex over each sentence that mentions visa/sponsor/citizen/clearance:
   - `no_sponsorship`: "unable to sponsor", "without current or future sponsorship", "must be a US citizen", "clearance required", "ITAR"
   - `sponsors`: "visa sponsorship available", "we sponsor H-1B", "immigration support"
   - `unclear`: both kinds appear
   - `unknown`: nothing said. This covers most postings, and it doesn't mean no.
2. **Employer history.** `data/h1b_sponsors.txt` is a short starter list. For real coverage download
   the [USCIS H-1B Employer Data Hub](https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub)
   CSV into `data/` and list it under `h1b_sponsor_files`. The loader picks up the employer and approval columns.

A company that files H-1Bs may still refuse to sponsor a particular role, so read the posting.

## How matching works

The score runs 0–100:
- 45% skill overlap: ~90 skills with aliases (`jobcollector/skills.py`) are pulled from your resume and from each job
- 30% title fit against `target_titles`
- 25% TF-IDF similarity between your resume and the description
- minus a penalty when the posting asks for many more years than `years_experience`, and a smaller one for "Senior"/"Lead" titles

The report lists the matched skills for each job, plus the skills it wants that your resume lacks.
Those are resume gaps worth checking before you apply.

## Run it daily

cron (8am every day):
```
0 8 * * * cd ~/job-collector && .venv/bin/python -m jobcollector --resume resumes/resume.pdf --since 24h >> reports/cron.log 2>&1
```
Open `reports/latest.html` afterwards.

Avoid scheduling this in GitHub Actions on this repo. It's public, so your resume and results would be public too.

## Tests

```
pip install pytest && python -m pytest -q
```
Each source adapter is tested against fixture payloads shaped like that API's real responses.
