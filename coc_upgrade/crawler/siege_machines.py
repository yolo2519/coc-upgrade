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


SIEGE_MACHINES: Dict[str, str] = {
    "Wall Wrecker": "Wall_Wrecker",
    "Battle Blimp": "Battle_Blimp",
    "Stone Slammer": "Stone_Slammer",
    "Siege Barracks": "Siege_Barracks",
    "Log Launcher": "Log_Launcher",
    "Flame Flinger": "Flame_Flinger",
    "Battle Drill": "Battle_Drill",
    "Troop Launcher": "Troop_Launcher",
}


def scrape_siege(name: str, slug: str) -> List[Dict[str, Any]]:
    url = BASE_URL + slug
    print(f"[INFO] Fetching siege machine: {name} -> {url}")
    
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    
    table = find_table_by_headers(
        soup,
        required_headers=["level", "cost", "time", "laboratory"]
    )
    
    if table is None:
        print(f"[WARN] Research table for {name} not found, skipping")
        return []
    
    header_row = table.find("tr")
    header_cells = header_row.find_all(["th", "td"])
    headers = [c.get_text(" ", strip=True) for c in header_cells]
    
    idx_level = find_column_index(headers, "level")
    
    idx_cost = find_column_index(headers, "research", "cost")
    if idx_cost < 0:
        idx_cost = find_column_index(headers, "upgrade", "cost")
    if idx_cost < 0:
        idx_cost = find_column_index(headers, "cost")
    
    idx_time = find_column_index(headers, "research", "time")
    if idx_time < 0:
        idx_time = find_column_index(headers, "upgrade", "time")
    if idx_time < 0:
        idx_time = find_column_index(headers, "time")
    
    idx_lab = find_column_index(headers, "laboratory", "level")
    if idx_lab < 0:
        idx_lab = find_column_index(headers, "laboratory", "required")
    
    if min(idx_level, idx_cost, idx_time, idx_lab) < 0:
        print(f"[WARN] Table headers for {name} are incomplete: {headers}. Skipping")
        return []
    
    rows = []
    
    for tr in table.find_all("tr")[1:]:
        cells = tr.find_all(["th", "td"])
        if len(cells) <= max(idx_level, idx_cost, idx_time, idx_lab):
            continue
        
        raw_level = cells[idx_level].get_text(strip=True)
        if not raw_level or not any(ch.isdigit() for ch in raw_level):
            continue
        
        level = clean_int(raw_level)
        raw_cost = cells[idx_cost].get_text(strip=True)
        cost_val = clean_int(raw_cost)
        raw_time = cells[idx_time].get_text(" ", strip=True)
        raw_lab = cells[idx_lab].get_text(strip=True)
        lab_level = clean_int(raw_lab)
        
        if cost_val == 0 and "n/a" in raw_cost.lower():
            continue
        
        rows.append({
            "name": name,
            "level": level,
            "gold": 0,
            "elixir": cost_val,
            "dark_elixir": 0,
            "builder_time_raw": "",
            "lab_time_raw": raw_time,
            "town_hall_required": None,
            "lab_level_required": lab_level,
            "hero_hall_level_required": None,
        })
    
    return rows


def crawl(output_dir: Path) -> None:
    all_data = []
    
    for name, slug in SIEGE_MACHINES.items():
        try:
            rows = scrape_siege(name, slug)
            all_data.extend(rows)
            sleep_between_requests()
        except Exception as e:
            print(f"[ERROR] Failed to fetch {name}: {e}")
    
    output_file = output_dir / "siege_machines.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Saved to: {output_file}, total records: {len(all_data)}")


if __name__ == "__main__":
    import sys
    
    output_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    crawl(output_dir)
