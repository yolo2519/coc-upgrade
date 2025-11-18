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


DARK_ELIXIR_TROOPS: List[Dict[str, str]] = [
    {"slug": "Minion", "name": "Minion"},
    {"slug": "Hog_Rider", "name": "Hog Rider"},
    {"slug": "Valkyrie", "name": "Valkyrie"},
    {"slug": "Golem", "name": "Golem"},
    {"slug": "Witch", "name": "Witch"},
    {"slug": "Lava_Hound", "name": "Lava Hound"},
    {"slug": "Bowler", "name": "Bowler"},
    {"slug": "Ice_Golem", "name": "Ice Golem"},
    {"slug": "Headhunter", "name": "Headhunter"},
]


def scrape_troop(slug: str, display_name: str) -> List[Dict[str, Any]]:
    url = BASE_URL + slug
    print(f"[INFO] Fetching dark troop: {display_name} -> {url}")
    
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    
    table = find_table_by_headers(
        soup,
        required_headers=["level", "research cost", "research time", "laboratory"]
    )
    
    if table is None:
        print(f"[WARN] Research table for {display_name} not found, skipping")
        return []
    
    header_row = table.find("tr")
    header_cells = header_row.find_all(["th", "td"])
    headers = [c.get_text(strip=True) for c in header_cells]
    
    idx_level = find_column_index(headers, "level")
    idx_cost = find_column_index(headers, "research", "cost")
    idx_time = find_column_index(headers, "research", "time")
    idx_lab = find_column_index(headers, "laboratory", "level")
    
    if min(idx_level, idx_cost, idx_time, idx_lab) < 0:
        print(f"[WARN] Table headers for {display_name} are incomplete, skipping")
        return []
    
    rows = []
    
    for tr in table.find_all("tr")[1:]:
        cells = tr.find_all(["th", "td"])
        if len(cells) <= max(idx_level, idx_cost, idx_time, idx_lab):
            continue
        
        raw_level = cells[idx_level].get_text(strip=True)
        if not raw_level or raw_level.lower() == "level":
            continue
        
        level = clean_int(raw_level)
        raw_cost = cells[idx_cost].get_text(strip=True)
        de_cost = clean_int(raw_cost)
        raw_time = cells[idx_time].get_text(" ", strip=True)
        raw_lab = cells[idx_lab].get_text(strip=True)
        lab_level = clean_int(raw_lab)
        
        rows.append({
            "name": display_name,
            "level": level,
            "gold": 0,
            "elixir": 0,
            "dark_elixir": de_cost,
            "builder_time_raw": "",
            "lab_time_raw": raw_time,
            "town_hall_required": None,
            "lab_level_required": lab_level,
            "hero_hall_level_required": None,
        })
    
    return rows


def crawl(output_dir: Path) -> None:
    all_data = []
    
    for troop in DARK_ELIXIR_TROOPS:
        slug = troop["slug"]
        name = troop["name"]
        try:
            rows = scrape_troop(slug, name)
            all_data.extend(rows)
            sleep_between_requests()
        except Exception as e:
            print(f"[ERROR] Failed to fetch {name}: {e}")
    
    output_file = output_dir / "troops_dark.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Saved to: {output_file}, total records: {len(all_data)}")


if __name__ == "__main__":
    import sys
    
    output_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    crawl(output_dir)
