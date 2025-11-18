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


DEFENSE_BUILDINGS: Dict[str, str] = {
    "Cannon": "Cannon",
    "Archer Tower": "Archer_Tower",
    "Mortar": "Mortar",
    "Air Defense": "Air_Defense",
    "Wizard Tower": "Wizard_Tower",
    "Air Sweeper": "Air_Sweeper",
    "Hidden Tesla": "Hidden_Tesla",
    "Bomb Tower": "Bomb_Tower",
    "X-Bow": "X-Bow",
    "Inferno Tower": "Inferno_Tower",
    "Eagle Artillery": "Eagle_Artillery",
}


def scrape_building(name: str, slug: str) -> List[Dict[str, Any]]:
    url = BASE_URL + slug
    print(f"[INFO] Fetching defense: {name} -> {url}")
    
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    
    table = find_table_by_headers(
        soup,
        required_headers=["level", "cost", "time", "town hall"]
    )
    
    if table is None:
        print(f"[WARN] {name}: Upgrade table not found, skipping")
        return []
    
    header_row = table.find("tr")
    headers = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]
    
    level_idx = find_column_index(headers, "level")
    cost_idx = find_column_index(headers, "build", "cost")
    if cost_idx < 0:
        cost_idx = find_column_index(headers, "upgrade", "cost")
    if cost_idx < 0:
        cost_idx = find_column_index(headers, "cost")
    time_idx = find_column_index(headers, "build", "time")
    if time_idx < 0:
        time_idx = find_column_index(headers, "upgrade", "time")
    th_idx = find_column_index(headers, "town", "hall")
    
    if any(idx < 0 for idx in [level_idx, cost_idx, time_idx, th_idx]):
        print(f"[WARN] {name}: Missing Level/Cost/Time/TH columns, skipping")
        return []
    
    rows_data = []
    
    for tr in table.find_all("tr")[1:]:
        tds = tr.find_all(["td", "th"])
        if len(tds) <= max(level_idx, cost_idx, time_idx, th_idx):
            continue
        
        level_text = tds[level_idx].get_text(strip=True)
        cost_cell = tds[cost_idx]
        time_text = tds[time_idx].get_text(strip=True)
        th_text = tds[th_idx].get_text(strip=True)
        
        level_nums = re.findall(r"\d+", level_text)
        if not level_nums:
            continue
        level = int(level_nums[0])
        
        th_nums = re.findall(r"\d+", th_text)
        th_required = int(th_nums[0]) if th_nums else None
        
        cost_val = clean_int(cost_cell.get_text(" ", strip=True))
        
        rows_data.append({
            "name": name,
            "level": level,
            "gold": cost_val,
            "elixir": 0,
            "dark_elixir": 0,
            "builder_time_raw": time_text,
            "lab_time_raw": "",
            "town_hall_required": th_required,
            "lab_level_required": None,
            "hero_hall_level_required": None,
        })
    
    return rows_data


def crawl(output_dir: Path) -> None:
    all_data = []
    
    for name, slug in DEFENSE_BUILDINGS.items():
        try:
            rows = scrape_building(name, slug)
            all_data.extend(rows)
            sleep_between_requests()
        except Exception as e:
            print(f"[ERROR] Failed to fetch {name}: {e}")
    
    output_file = output_dir / "defenses.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Saved to: {output_file}, total records: {len(all_data)}")


if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    output_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    crawl(output_dir)
