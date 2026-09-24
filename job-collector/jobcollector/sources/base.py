from __future__ import annotations

import logging
import time

import requests

log = logging.getLogger("jobcollector")

USER_AGENT = "job-collector/1.0 (personal job search; contact via GitHub)"


class SourceError(Exception):
    pass


def get_json(url: str, *, params=None, headers=None, timeout=25, retries=2):
    hdrs = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    last = None
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, params=params, headers=hdrs, timeout=timeout)
            if r.status_code == 404:
                raise SourceError(f"404 {url}")
            if r.status_code == 429 or r.status_code >= 500:
                last = SourceError(f"{r.status_code} {url}")
                time.sleep(2 ** attempt)
                continue
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            last = e
            time.sleep(2 ** attempt)
    raise SourceError(str(last))
