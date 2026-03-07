import re
from typing import Optional, Tuple

import requests
from bs4 import BeautifulSoup


def _extract_email(text: str) -> Optional[str]:
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match.group(0) if match else None


def _guess_location(text: str) -> Optional[str]:
    # Very naive heuristic: look for "Location:" style patterns
    for line in text.splitlines():
        if "location" in line.lower():
            return line.strip()
    return None


def _guess_poster_name(text: str) -> Optional[str]:
    # Placeholder heuristic; real implementation could parse LinkedIn blocks.
    return None


def scrape_linkedin_job(url: str) -> Tuple[str, str, Optional[str], Optional[str]]:
    """
    Basic text scrape for a LinkedIn job URL.

    Returns (jd_text, raw_html, location, contact_email).
    """
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    html = resp.text

    soup = BeautifulSoup(html, "html.parser")
    text = " ".join(soup.stripped_strings)

    email = _extract_email(text)
    location = _guess_location(text)

    return text, html, location, email

