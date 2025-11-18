from typing import List, Dict, Any
from pathlib import Path
import json

from ..models import UpgradeRecord
from .mappings import lab_level_to_th, hero_hall_to_th
from ..crawler.base import parse_time_to_str


def normalize_raw_data(raw_data: Dict[str, Any]) -> UpgradeRecord:
    town_hall = 0
    if raw_data.get("town_hall_required"):
        town_hall = raw_data["town_hall_required"]
    elif raw_data.get("lab_level_required"):
        town_hall = lab_level_to_th(raw_data["lab_level_required"])
    elif raw_data.get("hero_hall_level_required"):
        town_hall = hero_hall_to_th(raw_data["hero_hall_level_required"])
    
    builder_time = parse_time_to_str(raw_data.get("builder_time_raw", ""))
    lab_time = parse_time_to_str(raw_data.get("lab_time_raw", ""))
    
    return UpgradeRecord(
        name=raw_data["name"],
        level=raw_data["level"],
        town_hall=town_hall,
        gold=raw_data.get("gold", 0),
        elixir=raw_data.get("elixir", 0),
        dark_elixir=raw_data.get("dark_elixir", 0),
        builder_time=builder_time,
        lab_time=lab_time,
        count=None,
        lab_level_required=raw_data.get("lab_level_required"),
        hero_hall_level_required=raw_data.get("hero_hall_level_required"),
    )


def load_and_normalize(json_file: Path) -> List[UpgradeRecord]:
    with open(json_file, "r", encoding="utf-8") as f:
        raw_data_list = json.load(f)
    
    return [normalize_raw_data(raw_data) for raw_data in raw_data_list]


def filter_by_th(records: List[UpgradeRecord], town_hall: int) -> List[UpgradeRecord]:
    return [r for r in records if r.town_hall == town_hall]

