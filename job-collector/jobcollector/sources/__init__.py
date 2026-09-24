from . import ats, boards, keyed

# name -> (callable, kind). "company" sources are called once per company slug.
REGISTRY = {
    "greenhouse": (ats.greenhouse, "company"),
    "lever": (ats.lever, "company"),
    "ashby": (ats.ashby, "company"),
    "remotive": (boards.remotive, "search"),
    "remoteok": (boards.remoteok, "search"),
    "themuse": (boards.themuse, "search"),
    "hackernews": (boards.hackernews, "search"),
    "arbeitnow": (boards.arbeitnow, "search"),
    "jsearch": (keyed.jsearch, "search"),
    "adzuna": (keyed.adzuna, "search"),
    "jobspy": (keyed.jobspy, "search"),
}
