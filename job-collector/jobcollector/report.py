from __future__ import annotations

import csv
import html
import json
from datetime import datetime, timezone
from pathlib import Path

from .models import Job

_VISA_LABEL = {"sponsors": "Sponsors", "no_sponsorship": "No sponsorship",
               "unclear": "Unclear", "unknown": "Not stated"}


def _age(j: Job) -> str:
    h = j.age_hours()
    if h is None:
        return "?"
    return f"{int(h)}h" if h < 48 else f"{int(h // 24)}d"


def write_csv(jobs: list[Job], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["score", "new", "title", "company", "location", "posted_at", "age", "visa",
                    "known_h1b_sponsor", "visa_evidence", "matched_skills", "missing_skills",
                    "salary", "source", "url"])
        for j in jobs:
            w.writerow([j.score, "yes" if j.is_new else "", j.title, j.company, j.location,
                        j.posted_at.isoformat() if j.posted_at else "", _age(j), j.visa,
                        "yes" if j.known_sponsor else "", j.visa_evidence,
                        "; ".join(j.matched_skills), "; ".join(j.missing_skills),
                        j.salary, j.source, j.url])


def write_html(jobs: list[Job], path: Path, meta: dict) -> None:
    rows = []
    for j in jobs:
        e = html.escape
        visa_cls = j.visa
        sponsor = '<span class="pill ks" title="Employer appears in your H-1B sponsor list">H-1B filer</span>' if j.known_sponsor else ""
        rows.append(f"""<tr data-visa="{visa_cls}" data-new="{int(j.is_new)}" data-ks="{int(j.known_sponsor)}">
<td class="num">{j.score:.0f}</td>
<td><a href="{e(j.url)}" target="_blank" rel="noopener">{e(j.title)}</a>{' <span class="pill new">new</span>' if j.is_new else ''}
<div class="sub">{e(j.company)} · {e(j.location or '—')}{' · ' + e(j.salary) if j.salary else ''}</div></td>
<td class="num" data-sort="{j.age_hours() or 1e9:.1f}">{_age(j)}</td>
<td><span class="pill {visa_cls}" title="{e(j.visa_evidence)}">{_VISA_LABEL[j.visa]}</span> {sponsor}</td>
<td class="skills"><span class="ok">{e(', '.join(j.matched_skills))}</span>{'<div class="miss">missing: ' + e(', '.join(j.missing_skills[:8])) + '</div>' if j.missing_skills else ''}</td>
<td class="sub">{e(j.source)}</td></tr>""")

    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Job Matches</title>
<style>
:root{{--bg:#fff;--fg:#1a1a1a;--mut:#666;--line:#e5e5e5;--acc:#0b5fff;--ok:#137333;--bad:#b3261e;--warn:#8a5a00;--chip:#f2f2f2}}
@media (prefers-color-scheme:dark){{:root{{--bg:#111;--fg:#eee;--mut:#9a9a9a;--line:#2a2a2a;--acc:#7aa7ff;--ok:#6fcf8e;--bad:#ff8a80;--warn:#e0b050;--chip:#222}}}}
body{{margin:0;padding:16px;background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,sans-serif}}
h1{{font-size:20px;margin:0 0 4px}} .meta{{color:var(--mut);margin-bottom:12px}}
.bar{{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px}} .bar input[type=search]{{flex:1;min-width:180px;padding:6px 8px;border:1px solid var(--line);background:var(--bg);color:var(--fg);border-radius:6px}}
.bar label{{display:flex;gap:4px;align-items:center;color:var(--mut)}}
.wrap{{overflow-x:auto}} table{{border-collapse:collapse;width:100%;min-width:760px}}
th,td{{text-align:left;padding:8px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{cursor:pointer;user-select:none;font-weight:600;white-space:nowrap}} .num{{text-align:right;font-variant-numeric:tabular-nums}}
a{{color:var(--acc);text-decoration:none}} a:hover{{text-decoration:underline}}
.sub{{color:var(--mut);font-size:12px}} .skills{{font-size:12px;max-width:360px}} .ok{{color:var(--ok)}} .miss{{color:var(--mut)}}
.pill{{display:inline-block;padding:1px 7px;border-radius:10px;font-size:11px;background:var(--chip);white-space:nowrap}}
.pill.sponsors{{color:var(--ok)}} .pill.no_sponsorship{{color:var(--bad)}} .pill.unclear{{color:var(--warn)}} .pill.new{{color:var(--acc)}} .pill.ks{{color:var(--ok)}}
</style></head><body>
<h1>Job matches</h1>
<div class="meta">{len(jobs)} jobs · posted within {meta['since']} · sponsorship filter: {meta['sponsorship']} · generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC<br>
Sources: {html.escape(meta['sources'])}</div>
<div class="bar"><input type="search" id="q" placeholder="Filter by title, company, skill…">
<label><input type="checkbox" id="onlyNew"> new only</label>
<label><input type="checkbox" id="onlySpons"> sponsor signal only</label></div>
<div class="wrap"><table id="t"><thead><tr><th class="num">Score</th><th>Role</th><th class="num">Age</th><th>Visa</th><th>Your skills it wants</th><th>Source</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
<script>
const q=document.getElementById('q'),n=document.getElementById('onlyNew'),s=document.getElementById('onlySpons'),tb=document.querySelector('#t tbody');
function f(){{const v=q.value.toLowerCase();for(const r of tb.rows){{let ok=r.textContent.toLowerCase().includes(v);if(n.checked&&r.dataset.new!=='1')ok=false;if(s.checked&&r.dataset.visa!=='sponsors'&&r.dataset.ks!=='1')ok=false;r.style.display=ok?'':'none'}}}}
[q,n,s].forEach(e=>e.addEventListener('input',f));
document.querySelectorAll('#t th').forEach((th,i)=>th.addEventListener('click',()=>{{const rows=[...tb.rows];const dir=th.dataset.dir=th.dataset.dir==='a'?'d':'a';
rows.sort((a,b)=>{{const x=a.cells[i],y=b.cells[i];const xv=x.dataset.sort??x.textContent,yv=y.dataset.sort??y.textContent;const nx=parseFloat(xv),ny=parseFloat(yv);
const c=!isNaN(nx)&&!isNaN(ny)?nx-ny:xv.localeCompare(yv);return dir==='a'?c:-c}});rows.forEach(r=>tb.appendChild(r))}}));
</script></body></html>"""
    path.write_text(doc, encoding="utf-8")


def write_json(jobs: list[Job], path: Path) -> None:
    out = []
    for j in jobs:
        d = {k: v for k, v in j.__dict__.items() if k != "description"}
        d["posted_at"] = j.posted_at.isoformat() if j.posted_at else None
        out.append(d)
    path.write_text(json.dumps(out, indent=1), encoding="utf-8")
