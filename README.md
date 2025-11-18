# Clash of Clans Upgrade Data Scraper

Scrapes upgrade data from the Clash of Clans **Fandom** Wiki and generates Excel sheets
organized by Town Hall level.

## Project Structure

```
coc-upgrade/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/                 # Crawlers write raw JSON here
│   │   ├── defenses.json
│   │   ├── resources.json
│   │   ├── army_buildings.json
│   │   ├── troops_elixir.json
│   │   ├── troops_dark.json
│   │   ├── spells_elixir.json
│   │   ├── spells_dark.json
│   │   ├── heroes.json
│   │   └── siege_machines.json
│   └── processed/           # TH-specific Excel outputs
│       ├── TH11/
│       │   ├── defenses.xlsx
│       │   ├── resources.xlsx
│       │   ├── army_buildings.xlsx
│       │   ├── troops.xlsx
│       │   ├── spells.xlsx
│       │   ├── heroes.xlsx
│       │   ├── siege_machines.xlsx
│       │   └── all_merged.xlsx
│       └── TH10/
│           └── ...
├── coc_upgrade/
│   ├── __init__.py
│   ├── models.py            # Shared record structures (dataclasses)
│   ├── crawler/             # Fetch clean data from the Wiki
│   │   ├── __init__.py
│   │   ├── base.py          # Requests session + helpers
│   │   ├── defenses.py
│   │   ├── resources.py
│   │   ├── army_buildings.py
│   │   ├── troops_elixir.py
│   │   ├── troops_dark.py
│   │   ├── spells_elixir.py
│   │   ├── spells_dark.py
│   │   ├── heroes.py
│   │   └── siege_machines.py
│   ├── transform/           # Turn raw JSON into TH tables
│   │   ├── __init__.py
│   │   ├── mappings.py      # Lab level -> TH, Hero Hall -> TH
│   │   ├── normalize.py     # Normalize raw entries into UpgradeRecord
│   │   └── build_tables.py  # Load raw data + TH input, write Excel
│   └── cli.py               # Unified CLI entry point
└── scripts/
    ├── crawl_all.py         # Run every crawler once
    └── build_th_tables.py   # Build tables for a specific TH
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### 1. Fetch all data

```bash
# Use the CLI
python -m coc_upgrade.cli crawl

# Or run the helper script
python scripts/crawl_all.py
```

All data is saved under `data/raw/` as JSON files.

### 2. Generate tables for a specific Town Hall

```bash
# Use the CLI
python -m coc_upgrade.cli build 11

# Or run the helper script
python scripts/build_th_tables.py 11
```

This produces every Excel sheet inside `data/processed/TH11/`.

### 3. End-to-end example

```bash
# 1. Fetch data
python -m coc_upgrade.cli crawl

# 2. Build TH11 tables
python -m coc_upgrade.cli build 11

# 3. Build TH10 tables
python -m coc_upgrade.cli build 10
```

## Design Principles

1. **Separation of concerns**
   - `crawler/` fetches raw data from the Wiki and emits JSON
   - `transform/` consumes the raw data, applies TH filters, and writes Excel

2. **Unified data model**
   - Every entry conforms to the `UpgradeRecord` dataclass
   - Applies to buildings, troops, spells, heroes, and siege machines

3. **Flexibility**
   - Re-run crawlers any time to refresh only the raw JSON
   - Build tables for any Town Hall without another scraping pass

## Data Categories

- **Defenses**: Cannon, Archer Tower, Mortar, etc.
- **Resources**: Gold Mine, Elixir Collector, etc.
- **Army Buildings**: Army Camp, Barracks, Laboratory, etc.
- **Troops**: Includes Elixir and Dark Elixir troops
- **Spells**: Includes Elixir and Dark spells
- **Heroes**: Barbarian King, Archer Queen, etc.
- **Siege Machines**: Wall Wrecker, Battle Blimp, etc.

## Output Format

All Excel sheets use the same schema:

| Column | Description |
|--------|-------------|
| Name | Display name |
| Level | Level after the upgrade |
| TownHall | Required Town Hall |
| Gold | Gold cost |
| Elixir | Elixir cost |
| DE | Dark Elixir cost |
| Builder_Time | Build time (`Xd Yh Zm`) |
| Lab_Time | Research time (`Xd Yh Zm`) |
| Count | Max number available at that TH |

## Automatic Building Counts

The project scrapes the maximum number of each building per Town Hall and fills
the `Count` column automatically:

- **Defenses, Resources, Army Buildings**: Count is matched by TH + building name
- **Heroes, Siege Machines**: Always 1
- **Troops, Spells**: Not applicable (left empty)

Counts are stored in `data/raw/building_max_counts.json` with keys formatted as
`"TH|Building Name"`.
