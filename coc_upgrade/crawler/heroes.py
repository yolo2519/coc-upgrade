import json
import re
from pathlib import Path
from typing import List, Dict, Any

from bs4 import BeautifulSoup

from .base import (
    fetch_html,
    find_table_by_headers,
    find_column_index,
    parse_time_to_str,
    clean_int,
    sleep_between_requests,
    BASE_URL,
)


HEROES: Dict[str, Dict[str, str]] = {
    "Barbarian King": {
        "slug": "Barbarian_King",
        "currency": "de",
    },
    "Archer Queen": {
        "slug": "Archer_Queen",
        "currency": "de",
    },
    "Grand Warden": {
        "slug": "Grand_Warden",
        "currency": "elixir",
    },
    "Royal Champion": {
        "slug": "Royal_Champion",
        "currency": "de",
    },
}


def scrape_hero(name: str, slug: str, currency: str) -> List[Dict[str, Any]]:
    url = BASE_URL + slug
    print(f"[INFO] Fetching hero: {name} -> {url}")
    
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    
    table = find_table_by_headers(
        soup,
        required_headers=["level", "cost", "time", "hall"]
    )
    
    if table is None:
        table = find_table_by_headers(
            soup,
            required_headers=["level", "cost", "time", "laboratory"]
        )
    
    if table is None:
        print(f"[WARN] Upgrade table for {name} not found, skipping")
        return []
    
    header_row = table.find("tr")
    header_cells = header_row.find_all(["th", "td"])
    headers = [c.get_text(strip=True) for c in header_cells]
    
    idx_level = find_column_index(headers, "level")
    idx_cost = find_column_index(headers, "upgrade", "cost")
    if idx_cost < 0:
        idx_cost = find_column_index(headers, "research", "cost")
    if idx_cost < 0:
        idx_cost = find_column_index(headers, "cost")
    idx_time = find_column_index(headers, "upgrade", "time")
    if idx_time < 0:
        idx_time = find_column_index(headers, "research", "time")
    if idx_time < 0:
        idx_time = find_column_index(headers, "time")
    
    idx_hall = find_column_index(headers, "hero", "hall")
    if idx_hall < 0:
        idx_hall = find_column_index(headers, "town", "hall")
    if idx_hall < 0:
        idx_hall = find_column_index(headers, "laboratory", "level")
    
    if min(idx_level, idx_cost, idx_time) < 0:
        print(f"[WARN] Table headers for {name} are incomplete: {headers}. Skipping")
        return []
    
    use_lab_level = False
    if idx_hall >= 0:
        hall_header = headers[idx_hall].lower()
        use_lab_level = "laboratory" in hall_header
    
    rows = []
    
    for tr in table.find_all("tr")[1:]:
        cells = tr.find_all(["th", "td"])
        if len(cells) <= max(idx_level, idx_cost, idx_time, idx_hall):
            continue
        
        raw_level = cells[idx_level].get_text(strip=True)
        if not raw_level or not any(ch.isdigit() for ch in raw_level):
            continue
        
        level = clean_int(raw_level)
        raw_cost = cells[idx_cost].get_text(strip=True)
        cost_val = clean_int(raw_cost)
        raw_time = cells[idx_time].get_text(" ", strip=True)
        
        hall_level = None
        lab_level = None
        
        if idx_hall >= 0:
            raw_hall = cells[idx_hall].get_text(strip=True)
            if use_lab_level:
                lab_level = clean_int(raw_hall)
            else:
                hall_nums = re.findall(r"\d+", raw_hall)
                hall_level = int(hall_nums[0]) if hall_nums else None
        
        gold = elixir = de = 0
        if currency == "elixir":
            elixir = cost_val
        elif currency == "de":
            de = cost_val
        
        builder_time_raw = ""
        lab_time_raw = ""
        if use_lab_level:
            lab_time_raw = raw_time
        else:
            builder_time_raw = raw_time
        
        rows.append({
            "name": name,
            "level": level,
            "gold": gold,
            "elixir": elixir,
            "dark_elixir": de,
            "builder_time_raw": builder_time_raw,
            "lab_time_raw": lab_time_raw,
            "town_hall_required": None,
            "lab_level_required": lab_level,
            "hero_hall_level_required": hall_level,
        })
    
    return rows


def crawl(output_dir: Path) -> None:
    all_data = []
    
    for name, info in HEROES.items():
        slug = info["slug"]
        cur = info["currency"]
        try:
            rows = scrape_hero(name, slug, cur)
            all_data.extend(rows)
            sleep_between_requests()
        except Exception as e:
            print(f"[ERROR] Failed to fetch {name}: {e}")
    
    output_file = output_dir / "heroes.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Saved to: {output_file}, total records: {len(all_data)}")


if __name__ == "__main__":
    import sys
    
    output_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    crawl(output_dir)
