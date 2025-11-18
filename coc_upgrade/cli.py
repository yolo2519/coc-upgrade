import argparse
from pathlib import Path

from .crawler import (
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
from .transform.build_tables import build_th_tables


def crawl_all(raw_data_dir: Path) -> None:
    raw_data_dir.mkdir(parents=True, exist_ok=True)
    
    print("[INFO] Starting full data crawl...")
    
    defenses.crawl(raw_data_dir)
    resources.crawl(raw_data_dir)
    army_buildings.crawl(raw_data_dir)
    troops_elixir.crawl(raw_data_dir)
    troops_dark.crawl(raw_data_dir)
    spells_elixir.crawl(raw_data_dir)
    spells_dark.crawl(raw_data_dir)
    heroes.crawl(raw_data_dir)
    siege_machines.crawl(raw_data_dir)
    building_max_counts.crawl(raw_data_dir)
    
    print("[OK] Completed data crawl.")


def main():
    parser = argparse.ArgumentParser(
        description="Clash of Clans upgrade data crawler and table builder"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    crawl_parser = subparsers.add_parser("crawl", help="Fetch every category into raw JSON")
    crawl_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/raw"),
        help="Directory for raw JSON output (default: data/raw)"
    )
    
    build_parser = subparsers.add_parser("build", help="Generate Excel tables for a Town Hall")
    build_parser.add_argument(
        "town_hall",
        type=int,
        help="Town Hall level (e.g. 11)"
    )
    build_parser.add_argument(
        "--raw-dir",
        type=Path,
        default=Path("data/raw"),
        help="Directory containing raw JSON data (default: data/raw)"
    )
    build_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/processed"),
        help="Directory for generated Excel workbooks (default: data/processed)"
    )
    
    args = parser.parse_args()
    
    if args.command == "crawl":
        crawl_all(args.output_dir)
    elif args.command == "build":
        build_th_tables(args.raw_dir, args.output_dir, args.town_hall)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
