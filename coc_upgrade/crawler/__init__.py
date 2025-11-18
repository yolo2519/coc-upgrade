"""Crawler modules: fetch raw data from the Wiki and output JSON."""
from . import (
    defenses,
    resources,
    army_buildings,
    troops_elixir,
    troops_dark,
    spells_elixir,
    spells_dark,
    heroes,
    siege_machines,
    building_max_counts,
)

__all__ = [
    "defenses",
    "resources",
    "army_buildings",
    "troops_elixir",
    "troops_dark",
    "spells_elixir",
    "spells_dark",
    "heroes",
    "siege_machines",
    "building_max_counts",
]
