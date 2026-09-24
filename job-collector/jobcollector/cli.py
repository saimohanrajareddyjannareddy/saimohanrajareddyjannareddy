from __future__ import annotations

import argparse
import logging
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

from . import report
from .pipeline import collect, filter_and_rank
from .resume import read_resume
from .skills import extract_skills
from .sources import REGISTRY
from .store import Store
from .visa import load_sponsors

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCES = ["greenhouse", "lever", "ashby", "remotive", "remoteok", "themuse", "hackernews"]


def parse_since(s: str) -> int:
    m = re.fullmatch(r"(\d+)\s*([hdw])", s.strip().lower())
    if not m:
        raise argparse.ArgumentTypeError("use e.g. 24h, 3d, 1w")
    n, unit = int(m.group(1)), m.group(2)
    return n * {"h": 1, "d": 24, "w": 168}[unit]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="jobcollector", description="Collect fresh job postings and rank them against your resume.")
    ap.add_argument("command", nargs="?", default="run", choices=["run", "skills", "sources"])
    ap.add_argument("--config", default=str(ROOT / "config.yaml"))
    ap.add_argument("--resume", help="resume file (.pdf/.docx/.txt/.md); defaults to config resume_path")
    ap.add_argument("--since", type=parse_since, default="24h", help="posting age window: 24h, 3d, 1w (default 24h)")
    ap.add_argument("--sponsorship", choices=["any", "h1b", "strict"], default=None,
                    help="any: no visa filter · h1b: drop postings that say no sponsorship/citizens only (default) · "
                         "strict: only postings that say they sponsor, or known H-1B filers that don't say no")
    ap.add_argument("--sources", help=f"comma list; default from config. available: {','.join(REGISTRY)}")
    ap.add_argument("--min-score", type=float, default=None)
    ap.add_argument("--remote", action="store_true", help="remote roles only")
    ap.add_argument("--include-undated", action="store_true", help="keep postings with no date")
    ap.add_argument("--out", default=str(ROOT / "reports"))
    ap.add_argument("--top", type=int, default=25, help="rows to print in the terminal")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    if isinstance(args.since, str):
        args.since = parse_since(args.since)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s %(message)s")
    cfg = yaml.safe_load(Path(args.config).read_text()) or {}

    if args.command == "sources":
        for name, (_, kind) in REGISTRY.items():
            n = len((cfg.get("companies") or {}).get(name) or []) if kind == "company" else None
            print(f"{name:12} {kind:8} {f'{n} companies' if n is not None else ''}")
        return 0

    resume_path = args.resume or cfg.get("resume_path")
    if not resume_path:
        print("No resume given. Use --resume path/to/resume.pdf or set resume_path in config.yaml", file=sys.stderr)
        return 2
    resume_path = Path(resume_path)
    if not resume_path.is_absolute():
        resume_path = (Path(args.config).resolve().parent / resume_path)
    resume_text = read_resume(resume_path)

    if args.command == "skills":
        found = sorted(extract_skills(resume_text) | set((cfg.get("profile") or {}).get("extra_skills") or []))
        print(f"{len(found)} skills detected from {resume_path.name} (+ extra_skills in config):")
        print(", ".join(found))
        return 0

    sources = args.sources.split(",") if args.sources else (cfg.get("sources") or DEFAULT_SOURCES)
    unknown = [s for s in sources if s not in REGISTRY]
    if unknown:
        print(f"unknown sources: {unknown}", file=sys.stderr)
        return 2
    sponsorship = args.sponsorship or (cfg.get("filters") or {}).get("sponsorship", "h1b")
    min_score = args.min_score if args.min_score is not None else (cfg.get("filters") or {}).get("min_score", 35)

    base = Path(args.config).resolve().parent
    sponsor_files = [base / p for p in (cfg.get("h1b_sponsor_files") or ["data/h1b_sponsors.txt"])]
    sponsors = load_sponsors(sponsor_files)

    logging.info("collecting from %s ...", ", ".join(sources))
    raw, stats = collect(cfg, sources, args.since)
    jobs = filter_and_rank(raw, resume_text, cfg, since_hours=args.since, sponsorship=sponsorship,
                           sponsors=sponsors, min_score=min_score, remote_only=args.remote,
                           include_undated=args.include_undated)

    Store(base / "data" / "seen.sqlite").mark(jobs)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    window = f"{args.since}h" if args.since < 48 else f"{args.since // 24}d"
    meta = {"since": window, "sponsorship": sponsorship,
            "sources": ", ".join(f"{k}={v}" for k, v in sorted(stats.items()) if not v.startswith(("skipped", "error")))}
    report.write_html(jobs, out / f"jobs_{stamp}.html", meta)
    report.write_csv(jobs, out / f"jobs_{stamp}.csv")
    report.write_json(jobs, out / "latest.json")
    report.write_html(jobs, out / "latest.html", meta)

    failed = {k: v for k, v in stats.items() if not v.isdigit()}
    print(f"\nFetched {len(raw)} postings from {len(stats) - len(failed)}/{len(stats)} feeds; "
          f"{len(jobs)} match (window {window}, sponsorship={sponsorship}, min score {min_score}).")
    if failed:
        print(f"{len(failed)} feeds skipped/failed (run with -v for details): " + ", ".join(sorted(failed)[:12])
              + (" ..." if len(failed) > 12 else ""))
    print(f"\n{'score':>5}  {'new':3}  {'visa':8}  {'age':>4}  title — company")
    for j in jobs[: args.top]:
        visa = {"sponsors": "SPONSOR", "unclear": "unclear", "unknown": "-"}.get(j.visa, j.visa)
        if j.known_sponsor and j.visa != "sponsors":
            visa += "*"
        print(f"{j.score:5.0f}  {'NEW' if j.is_new else '':3}  {visa:8}  {report._age(j):>4}  {j.title} — {j.company}")
    print("\n* = employer is in your H-1B filer list but the posting doesn't mention sponsorship")
    print(f"Report: {out / f'jobs_{stamp}.html'}\nCSV:    {out / f'jobs_{stamp}.csv'}")
    return 0
