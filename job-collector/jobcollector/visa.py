"""Visa-sponsorship classification.

Two signals:
1. What the posting text says ("we sponsor H-1B" vs "no sponsorship",
   "US citizens only", security clearance, ITAR).
2. Whether the employer is a known H-1B sponsor (data/h1b_sponsors.txt, or
   the USCIS H-1B Employer Data Hub CSV if you download it).

Most postings say nothing either way, so "unknown" is the common case and
does not mean "no".
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

_NEG = [
    r"(?:unable|not able|cannot|can ?not|can't|will not|won't|do not|does not|don't|are not able|is not able)"
    r"(?: to)?(?: currently)?(?: provide| offer| support| sponsor| consider)?[^.]{0,40}?(?:visa |immigration )?sponsor",
    r"\bno (?:visa |h-?1b |immigration )?sponsorship",
    r"sponsorship (?:is |will )?(?:not|n't) (?:be )?(?:available|provided|offered|possible|supported)",
    r"without (?:the )?(?:need|requirement)[^.]{0,30}sponsorship",
    r"not (?:be )?eligible for (?:visa |immigration )?sponsorship",
    r"must be (?:a )?(?:u\.?s\.? citizen|united states citizen|us person|green card holder|permanent resident)",
    r"(?:u\.?s\.?|united states) citizenship (?:is )?required",
    r"(?:only|solely) (?:u\.?s\.?|us) citizens",
    r"(?:active|current|obtain|maintain)[^.]{0,30}(?:security|secret|ts/sci|top secret) clearance",
    r"\bclearance (?:is )?required",
    r"\bitar\b",
    r"\bno visas?\b",
    r"not (?:offering|providing) (?:visa )?sponsorship",
]
_POS = [
    r"visa sponsorship (?:is )?(?:available|provided|offered|supported|possible)",
    r"(?:will|can|able to|happy to|open to|do|does|we) (?:also )?sponsor(?:s)?\b",
    r"sponsor(?:ship)?[^.]{0,20}(?:h-?1b|h1-b|visas?|green cards?)",
    r"h-?1b (?:transfer|sponsorship|visa)",
    r"(?:offer|provide)s? (?:visa|immigration) (?:sponsorship|support)",
    r"immigration support",
    r"\bvisa(?:s)? (?:ok|welcome|available|friendly)\b",
]
_NEG_RX = re.compile("|".join(f"(?:{p})" for p in _NEG), re.I)
_POS_RX = re.compile("|".join(f"(?:{p})" for p in _POS), re.I)
_TOPIC_RX = re.compile(r"sponsor|visa|h-?1b|citizen|clearance|itar|immigration|work authori[sz]ation", re.I)
_VISA_WORD_RX = re.compile(r"visa|h-?1b|h1-b|immigration|green card|work authori[sz]ation|\bopt\b|stem opt", re.I)
_SENT_SPLIT = re.compile(r"(?<=[.!?\n])\s+")
# HN convention: a bare "VISA" field in the pipe-separated header line.
_HN_VISA = re.compile(r"\|\s*(?:onsite|remote|hybrid)?[^|]{0,20}\bVISA\b(?! not| n/a)", re.S)


def classify(text: str) -> tuple[str, str]:
    """Returns (status, evidence). status: sponsors | no_sponsorship | unclear | unknown."""
    pos_ev = neg_ev = ""
    for sent in _SENT_SPLIT.split(text):
        if not _TOPIC_RX.search(sent):
            continue
        s = sent.strip()[:240]
        if _NEG_RX.search(sent):
            neg_ev = neg_ev or s
        elif _POS_RX.search(sent) and _VISA_WORD_RX.search(sent):
            pos_ev = pos_ev or s
    header = text.split("\n", 1)[0]
    if not pos_ev and not neg_ev and _HN_VISA.search(header):
        pos_ev = "HN post header lists VISA"
    if pos_ev and neg_ev:
        return "unclear", f"+ {pos_ev} / - {neg_ev}"
    if neg_ev:
        return "no_sponsorship", neg_ev
    if pos_ev:
        return "sponsors", pos_ev
    return "unknown", ""


_SUFFIX = re.compile(r"\b(inc|llc|l\.l\.c|corp|corporation|co|company|ltd|limited|plc|lp|llp|pbc|technologies|technology|labs|ai|hq|usa|us|the)\b\.?", re.I)


def norm_company(name: str) -> str:
    s = _SUFFIX.sub(" ", name.lower())
    return re.sub(r"[^a-z0-9]+", "", s)


def load_sponsors(paths: list[str | Path], min_approvals: int = 1) -> set[str]:
    """Loads employer names from .txt (one per line) or USCIS Employer Data Hub .csv files."""
    out: set[str] = set()
    for path in paths:
        p = Path(path)
        if not p.exists():
            continue
        if p.suffix.lower() == ".csv":
            with p.open(newline="", encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                cols = reader.fieldnames or []
                name_col = next((c for c in cols if "employer" in c.lower()), None)
                appr_cols = [c for c in cols if "approval" in c.lower()]
                if not name_col:
                    continue
                for row in reader:
                    total = 0
                    for c in appr_cols:
                        try:
                            total += int(str(row.get(c) or "0").replace(",", ""))
                        except ValueError:
                            pass
                    if total >= min_approvals or not appr_cols:
                        out.add(norm_company(row[name_col] or ""))
        else:
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.split("#", 1)[0].strip()
                if line:
                    out.add(norm_company(line))
    out.discard("")
    return out
