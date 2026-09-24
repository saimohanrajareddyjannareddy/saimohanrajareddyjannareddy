from __future__ import annotations

import re

_STATES = ("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY "
           "NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC").split()
_STATE_NAMES = ["alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut", "delaware",
                "florida", "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky",
                "louisiana", "maine", "maryland", "massachusetts", "michigan", "minnesota", "mississippi",
                "missouri", "montana", "nebraska", "nevada", "new hampshire", "new jersey", "new mexico",
                "new york", "north carolina", "north dakota", "ohio", "oklahoma", "oregon", "pennsylvania",
                "rhode island", "south carolina", "south dakota", "tennessee", "texas", "utah", "vermont",
                "virginia", "washington", "west virginia", "wisconsin", "wyoming"]
_CITIES = ["san francisco", "sf", "bay area", "palo alto", "mountain view", "menlo park", "sunnyvale",
           "san jose", "seattle", "bellevue", "nyc", "new york", "boston", "cambridge", "austin", "chicago",
           "los angeles", "denver", "atlanta", "st. louis", "st louis", "saint louis", "kansas city",
           "dallas", "houston", "miami", "pittsburgh", "philadelphia", "san diego", "portland", "raleigh",
           "washington d.c.", "redmond", "irvine", "salt lake city", "minneapolis", "detroit", "phoenix"]
_US_RX = re.compile(
    r"\b(?:united states|u\.s\.a?\.?|usa|us|north america|americas)\b"
    r"|,\s*(?:" + "|".join(_STATES) + r")\b"
    r"|\b(?:" + "|".join(re.escape(s) for s in _STATE_NAMES + _CITIES) + r")\b",
    re.I,
)
_NON_US_RX = re.compile(
    r"\b(?:uk|united kingdom|london|england|ireland|dublin|germany|berlin|munich|france|paris|spain|"
    r"netherlands|amsterdam|poland|india|bangalore|bengaluru|hyderabad|pune|canada|toronto|vancouver|"
    r"montreal|mexico|brazil|argentina|singapore|japan|tokyo|australia|sydney|israel|tel aviv|emea|apac|"
    r"latam|europe|switzerland|zurich|sweden|portugal|lisbon|philippines|korea|seoul|china|remote - eu)\b",
    re.I,
)


def is_us(location: str) -> bool:
    """True if the posting can plausibly be done from the US.
    Multi-location strings count if any part is US; bare 'Remote' counts."""
    loc = location.strip()
    if not loc:
        return True  # unknown; don't throw it away
    if _US_RX.search(loc):
        return True
    if _NON_US_RX.search(loc):
        return False
    return bool(re.search(r"\b(remote|anywhere|worldwide|global)\b", loc, re.I))


def is_remote(job_location: str, flag) -> bool:
    return bool(flag) or bool(re.search(r"\bremote\b", job_location, re.I))
