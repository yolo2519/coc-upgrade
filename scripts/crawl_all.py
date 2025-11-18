#!/usr/bin/env python3
"""Fetch every category and write raw JSON files."""
import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from coc_upgrade.cli import crawl_all


if __name__ == "__main__":
    raw_data_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw")
    crawl_all(raw_data_dir)
