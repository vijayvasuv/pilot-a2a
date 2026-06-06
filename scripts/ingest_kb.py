"""Build the local KB search index from markdown articles."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.rag import ingest_kb


def main():
    count = ingest_kb()
    print(f"Indexed {count} KB chunks into local KB index.")


if __name__ == "__main__":
    main()
