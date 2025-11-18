import json
import re
from pathlib import Path
from typing import Dict

from .base import fetch_html, BASE_URL


URL = "https://clashofclans.fandom.com/wiki/Town_Hall"


def extract_number(text: str) -> int:
    nums = re.findall(r"\d+", text)
    return int(nums[0]) if nums else 0


def parse_max_count_table(table) -> Dict[tuple, int]:
    result = {}
    
    header_row = table.find("tr")
    head_cells = header_row.find_all(["th", "td"])
    headers = [c.get_text(" ", strip=True) for c in head_cells]
    
    if len(headers) < 2:
        return {}
    
    building_names = headers[1:]
    
    for tr in table.find_all("tr")[1:]:
        cells = tr.find_all(["th", "td"])
        if len(cells) < len(building_names) + 1:
            continue
        
        th_text = cells[0].get_text(strip=True)
        th_level = extract_number(th_text)
        if th_level == 0:
            continue
        
        for idx, bname in enumerate(building_names, start=1):
            if idx >= len(cells):
                continue
            cell_text = cells[idx].get_text(strip=True)
            count = extract_number(cell_text)
            if count > 0:
                bname_clean = bname.strip()
                result[(th_level, bname_clean)] = count
    
    return result


def crawl(output_dir: Path) -> None:
    print("[INFO] Fetching max building counts...")
    
    html = fetch_html(URL)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    
    tables = soup.find_all("table", class_="wikitable")
    
    keyword_list = [
        "maximum number of buildings",
        "maximum number of army buildings",
        "maximum number of resource buildings",
        "maximum number",
    ]
    
    total_map = {}
    
    for tbl in tables:
        caption = tbl.find("caption")
        caption_text = caption.get_text(strip=True).lower() if caption else ""
        
        if any(keyword in caption_text for keyword in keyword_list):
            tbl_name = caption_text
            part = parse_max_count_table(tbl)
            total_map.update(part)
            print(f"[INFO] Parsed table: {tbl_name} ({len(part)} entries)")
    
    output_file = output_dir / "building_max_counts.json"
    
    output_dict = {
        f"{th}|{bname}": count
        for (th, bname), count in total_map.items()
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_dict, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Saved to: {output_file}, total mappings: {len(output_dict)}")


def load_max_counts(max_counts_file: Path) -> Dict[tuple, int]:
    if not max_counts_file.exists():
        return {}
    
    with open(max_counts_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    result = {}
    for key, count in data.items():
        parts = key.split("|", 1)
        if len(parts) == 2:
            th_level = int(parts[0])
            building_name = parts[1]
            result[(th_level, building_name)] = count
    
    return result


if __name__ == "__main__":
    import sys
    
    output_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    crawl(output_dir)
