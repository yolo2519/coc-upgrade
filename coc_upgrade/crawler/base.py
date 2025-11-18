import re
import time
from typing import List, Optional

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://clashofclans.fandom.com/wiki/"

_session = None


def get_session() -> requests.Session:
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        })
    return _session


def fetch_html(url: str, timeout: int = 15) -> str:
    session = get_session()
    resp = session.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def parse_time_to_str(time_text: str) -> str:
    """Normalize wiki time strings to the 'Xd Yh Zm' format."""
    text = time_text.strip().lower()
    if not text or text in {"-", "—"}:
        return ""
    if "instant" in text:
        return ""

    days = hours = minutes = 0

    m = re.search(r"(\d+)\s*d", text) or re.search(r"(\d+)\s*day", text)
    if m:
        days = int(m.group(1))

    m = re.search(r"(\d+)\s*h", text) or re.search(r"(\d+)\s*hour", text)
    if m:
        hours = int(m.group(1))

    m = re.search(r"(\d+)\s*m", text) or re.search(r"(\d+)\s*min", text)
    if m:
        minutes = int(m.group(1))

    parts: List[str] = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")

    return " ".join(parts)


def clean_int(text: str) -> int:
    """Extract digits and convert to int."""
    if not text:
        return 0
    t = text.strip()
    if t.upper() == "N/A":
        return 0
    digits = re.sub(r"[^\d]", "", t)
    return int(digits) if digits else 0


def find_table_by_headers(
    soup: BeautifulSoup,
    required_headers: List[str],
    table_class: str = "wikitable"
) -> Optional[BeautifulSoup]:
    tables = soup.find_all("table", class_=table_class)
    
    for table in tables:
        header_row = table.find("tr")
        if not header_row:
            continue
        
        header_cells = header_row.find_all(["th", "td"])
        headers = [c.get_text(strip=True) for c in header_cells]
        headers_lower = [h.lower() for h in headers]
        header_str = " | ".join(headers_lower)
        
        if all(keyword.lower() in header_str for keyword in required_headers):
            return table
    
    return None


def find_column_index(headers: List[str], *keywords: str) -> int:
    headers_lower = [h.lower() for h in headers]
    for idx, header in enumerate(headers_lower):
        if all(kw.lower() in header for kw in keywords):
            return idx
    return -1


def sleep_between_requests(seconds: float = 1.5):
    time.sleep(seconds)
