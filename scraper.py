"""Simple scraper for Jobindex API results.

This script fetches job listings from a given Jobindex API endpoint
and prints a readable summary of each job.
"""

from __future__ import annotations

import json
import sys
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional


DEFAULT_URL = (
    "https://www.jobindex.dk/api/jobsearch/v3/?address=Skovvej+67%2C+9510+Arden"
    "&jobage=1&latitude=56.776759306331&longitude=9.859810066344&radius=40"
    "&sort=score&page=1&include_html=1&include_skyscraper=1"
)


@dataclass
class JobPosting:
    """Lightweight container for key job fields."""

    headline: str
    company: Optional[str]
    area: Optional[str]
    apply_deadline: Optional[str]
    apply_url: Optional[str]
    distance_km: Optional[float]

    @classmethod
    def from_api_payload(cls, payload: Dict[str, Any]) -> "JobPosting":
        company = payload.get("company") or {}
        distance = _parse_distance(payload.get("distance"))
        return cls(
            headline=payload.get("headline") or "(no title)",
            company=company.get("name"),
            area=payload.get("area"),
            apply_deadline=_format_deadline(payload.get("apply_deadline")),
            apply_url=payload.get("apply_url") or payload.get("url"),
            distance_km=distance,
        )


def _format_deadline(deadline: Optional[str]) -> Optional[str]:
    if not deadline:
        return None
    try:
        dt = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
    except ValueError:
        return deadline
    return dt.strftime("%Y-%m-%d %H:%M %Z").strip()


def fetch(url: str = DEFAULT_URL, timeout: int = 20) -> Dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
    except urllib.error.URLError as exc:  # pragma: no cover - network errors
        raise RuntimeError(f"Failed to fetch data: {exc}") from exc
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Received invalid JSON from Jobindex") from exc


def parse_jobs(payload: Dict[str, Any]) -> List[JobPosting]:
    results: Iterable[Dict[str, Any]] = payload.get("results") or []
    return [JobPosting.from_api_payload(job) for job in results]


def print_jobs(jobs: Iterable[JobPosting]) -> None:
    for job in jobs:
        print(job.headline)
        if job.company:
            print(f"  Company: {job.company}")
        if job.area:
            print(f"  Area: {job.area}")
        if job.distance_km is not None:
            print(f"  Distance: {job.distance_km:.1f} km")
        if job.apply_deadline:
            print(f"  Deadline: {job.apply_deadline}")
        if job.apply_url:
            print(f"  Apply: {job.apply_url}")
        print()


def _parse_distance(distance: Optional[Any]) -> Optional[float]:
    if distance in (None, ""):
        return None
    if isinstance(distance, (int, float)):
        return float(distance)
    if isinstance(distance, str):
        cleaned = distance.strip().lower().replace(" km", "")
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def set_query_param(url: str, key: str, value: str) -> str:
    parsed = urlparse(url)
    q = parse_qs(parsed.query)
    q[key] = [value]
    new_query = urlencode(q, doseq=True)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))


def main(args: List[str]) -> int:
    base_url = args[0] if args else DEFAULT_URL
    # Normalize to start at page=1
    page1_url = set_query_param(base_url, "page", "1")

    first_payload = fetch(page1_url)
    total_pages = int(first_payload.get("total_pages") or 1)

    all_jobs: List[JobPosting] = []
    all_jobs.extend(parse_jobs(first_payload))

    if total_pages > 1:
        for page in range(2, total_pages + 1):
            page_url = set_query_param(base_url, "page", str(page))
            payload = fetch(page_url)
            all_jobs.extend(parse_jobs(payload))

    if not all_jobs:
        print("No job postings found.")
        return 0

    print(f"Total jobs: {len(all_jobs)}\n")
    print_jobs(all_jobs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

