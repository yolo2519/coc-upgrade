#!/usr/bin/env python3
"""Generate Excel tables for a specific Town Hall."""
import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from coc_upgrade.transform.build_tables import build_th_tables


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python build_th_tables.py <TH> [raw_dir] [output_dir]")
        print("Example: python build_th_tables.py 11")
        sys.exit(1)
    
    town_hall = int(sys.argv[1])
    raw_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/raw")
    output_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("data/processed")
    
    build_th_tables(raw_dir, output_dir, town_hall)
