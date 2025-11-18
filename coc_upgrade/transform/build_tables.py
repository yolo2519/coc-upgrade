from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd

from ..models import UpgradeRecord
from .normalize import load_and_normalize, filter_by_th
from ..crawler.building_max_counts import load_max_counts


def build_category_table(
    records: List[UpgradeRecord],
    category_name: str,
    output_file: Path,
    max_counts: Optional[Dict[tuple, int]] = None,
    town_hall: Optional[int] = None
) -> None:
    if not records:
        print(f"[WARN] No data for category {category_name}, skipping")
        return
    
    if max_counts is not None and town_hall is not None:
        for record in records:
            if record.count is None:
                key = (town_hall, record.name)
                if key in max_counts:
                    record.count = max_counts[key]
                else:
                    for (th, bname), count in max_counts.items():
                        if th == town_hall and bname.lower() == record.name.lower():
                            record.count = count
                            break
    
    rows = [r.to_dict() for r in records]
    df = pd.DataFrame(rows)
    
    df = df.rename(columns={
        "name": "Name",
        "level": "Level",
        "town_hall": "TownHall",
        "gold": "Gold",
        "elixir": "Elixir",
        "dark_elixir": "DE",
        "builder_time": "Builder_Time",
        "lab_time": "Lab_Time",
        "count": "Count",
    })
    
    columns_order = [
        "Name", "Level", "TownHall", "Gold", "Elixir", "DE",
        "Builder_Time", "Lab_Time", "Count"
    ]
    df = df[columns_order]
    
    df = df.sort_values(by=["Name", "Level"]).reset_index(drop=True)
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_file, index=False)
    print(f"[OK] Saved: {output_file} ({len(df)} rows)")


def build_th_tables(
    raw_data_dir: Path,
    output_dir: Path,
    town_hall: int
) -> None:
    th_dir = output_dir / f"TH{town_hall}"
    th_dir.mkdir(parents=True, exist_ok=True)
    
    max_counts_file = raw_data_dir / "building_max_counts.json"
    max_counts = load_max_counts(max_counts_file) if max_counts_file.exists() else {}
    if max_counts:
        print(f"[INFO] Loaded max building counts ({len(max_counts)} entries)")
    
    category_files = {
        "defenses.json": ("defenses", "defenses.xlsx"),
        "resources.json": ("resources", "resources.xlsx"),
        "army_buildings.json": ("army_buildings", "army_buildings.xlsx"),
        "troops_elixir.json": ("troops_elixir", "troops.xlsx"),
        "troops_dark.json": ("troops_dark", None),
        "spells_elixir.json": ("spells_elixir", "spells.xlsx"),
        "spells_dark.json": ("spells_dark", None),
        "heroes.json": ("heroes", "heroes.xlsx"),
        "siege_machines.json": ("siege_machines", "siege_machines.xlsx"),
    }
    
    all_records: Dict[str, List[UpgradeRecord]] = {}
    
    for json_file_name, (category_key, _) in category_files.items():
        json_file = raw_data_dir / json_file_name
        if not json_file.exists():
            print(f"[WARN] Missing file: {json_file}, skipping")
            continue
        
        try:
            records = load_and_normalize(json_file)
            filtered = filter_by_th(records, town_hall)
            all_records[category_key] = filtered
            print(f"[INFO] {category_key}: loaded {len(records)} rows, {len(filtered)} after TH filter")
        except Exception as e:
            print(f"[ERROR] Failed to process {json_file}: {e}")
    
    if "defenses" in all_records:
        build_category_table(
            all_records["defenses"],
            "defenses",
            th_dir / "defenses.xlsx",
            max_counts=max_counts,
            town_hall=town_hall
        )
    
    if "resources" in all_records:
        build_category_table(
            all_records["resources"],
            "resources",
            th_dir / "resources.xlsx",
            max_counts=max_counts,
            town_hall=town_hall
        )
    
    if "army_buildings" in all_records:
        build_category_table(
            all_records["army_buildings"],
            "army_buildings",
            th_dir / "army_buildings.xlsx",
            max_counts=max_counts,
            town_hall=town_hall
        )
    
    troops_all = []
    if "troops_elixir" in all_records:
        troops_all.extend(all_records["troops_elixir"])
    if "troops_dark" in all_records:
        troops_all.extend(all_records["troops_dark"])
    if troops_all:
        build_category_table(
            troops_all,
            "troops",
            th_dir / "troops.xlsx",
            max_counts=None,
            town_hall=None
        )
    
    spells_all = []
    if "spells_elixir" in all_records:
        spells_all.extend(all_records["spells_elixir"])
    if "spells_dark" in all_records:
        spells_all.extend(all_records["spells_dark"])
    if spells_all:
        build_category_table(
            spells_all,
            "spells",
            th_dir / "spells.xlsx",
            max_counts=None,
            town_hall=None
        )
    
    if "heroes" in all_records:
        for record in all_records["heroes"]:
            if record.count is None:
                record.count = 1
        build_category_table(
            all_records["heroes"],
            "heroes",
            th_dir / "heroes.xlsx",
            max_counts=None,
            town_hall=None
        )
    
    if "siege_machines" in all_records:
        for record in all_records["siege_machines"]:
            if record.count is None:
                record.count = 1
        build_category_table(
            all_records["siege_machines"],
            "siege_machines",
            th_dir / "siege_machines.xlsx",
            max_counts=None,
            town_hall=None
        )
    
    all_merged = []
    for records in all_records.values():
        all_merged.extend(records)
    
    if all_merged:
        build_category_table(
            all_merged,
            "all_merged",
            th_dir / "all_merged.xlsx",
            max_counts=max_counts,
            town_hall=town_hall
        )
