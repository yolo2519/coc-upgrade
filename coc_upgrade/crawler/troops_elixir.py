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


ELIXIR_TROOPS: List[Dict[str, str]] = [
    {"slug": "Barbarian", "name": "Barbarian"},
    {"slug": "Archer", "name": "Archer"},
    {"slug": "Giant", "name": "Giant"},
    {"slug": "Goblin", "name": "Goblin"},
    {"slug": "Wall_Breaker", "name": "Wall Breaker"},
    {"slug": "Balloon", "name": "Balloon"},
    {"slug": "Wizard", "name": "Wizard"},
    {"slug": "Healer", "name": "Healer"},
    {"slug": "Dragon", "name": "Dragon"},
    {"slug": "P.E.K.K.A", "name": "P.E.K.K.A"},
    {"slug": "Baby_Dragon", "name": "Baby Dragon"},
    {"slug": "Miner", "name": "Miner"},
    {"slug": "Electro_Dragon", "name": "Electro Dragon"},
    {"slug": "Yeti", "name": "Yeti"},
    {"slug": "Dragon_Rider", "name": "Dragon Rider"},
    {"slug": "Electro_Titan", "name": "Electro Titan"},
    {"slug": "Root_Rider", "name": "Root Rider"},
    {"slug": "Thrower", "name": "Thrower"},
    {"slug": "Apprentice_Warden", "name": "Apprentice Warden"},
]


def scrape_troop(slug: str, display_name: str) -> List[Dict[str, Any]]:
    url = BASE_URL + slug
    print(f"[INFO] Fetching elixir troop: {display_name} -> {url}")
    
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
        cost_cell = cells[idx_cost]
        raw_cost = cost_cell.get_text(strip=True)
        cost_val = clean_int(raw_cost)
        
        cost_html = str(cost_cell).lower()
        is_dark_elixir = (
            display_name == "Apprentice Warden" or
            "dark" in cost_html and "elixir" in cost_html or
            "de.png" in cost_html or
            "darkelixir" in cost_html
        )
        
        raw_time = cells[idx_time].get_text(" ", strip=True)
        raw_lab = cells[idx_lab].get_text(strip=True)
        lab_level = clean_int(raw_lab)
        
        gold = elixir = de = 0
        if is_dark_elixir:
            de = cost_val
        else:
            elixir = cost_val
        
        rows.append({
            "name": display_name,
            "level": level,
            "gold": gold,
            "elixir": elixir,
            "dark_elixir": de,
            "builder_time_raw": "",
            "lab_time_raw": raw_time,
            "town_hall_required": None,
            "lab_level_required": lab_level,
            "hero_hall_level_required": None,
        })
    
    return rows


def crawl(output_dir: Path) -> None:
    all_data = []
    
    for troop in ELIXIR_TROOPS:
        slug = troop["slug"]
        name = troop["name"]
        try:
            rows = scrape_troop(slug, name)
            all_data.extend(rows)
            sleep_between_requests()
        except Exception as e:
            print(f"[ERROR] Failed to fetch {name}: {e}")
    
    output_file = output_dir / "troops_elixir.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Saved to: {output_file}, total records: {len(all_data)}")


if __name__ == "__main__":
    import sys
    
    output_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    crawl(output_dir)
