from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class UpgradeRecord:
    """Normalized upgrade record."""
    name: str
    level: int
    town_hall: int
    
    gold: int = 0
    elixir: int = 0
    dark_elixir: int = 0
    
    builder_time: str = ""
    lab_time: str = ""
    
    count: Optional[int] = None
    
    lab_level_required: Optional[int] = None
    hero_hall_level_required: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if d.get("count") is None:
            d["count"] = ""
        return d


@dataclass
class RawUpgradeData:
    """Raw data scraped directly from the Wiki."""
    name: str
    level: int
    
    gold: int = 0
    elixir: int = 0
    dark_elixir: int = 0
    
    builder_time_raw: str = ""
    lab_time_raw: str = ""
    
    town_hall_required: Optional[int] = None
    lab_level_required: Optional[int] = None
    hero_hall_level_required: Optional[int] = None
    
    metadata: Optional[Dict[str, Any]] = None
