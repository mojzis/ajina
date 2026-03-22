"""Assemble the final static site from templates and generated assets.

Copies templates to site/, verifies all referenced assets exist,
and reports any missing files.
"""

import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", action="store_true", help="Open site in browser after build")
    args = parser.parse_args()

    # TODO: Implement in Phase 3
    templates_dir = PROJECT_ROOT / "templates"
    site_dir = PROJECT_ROOT / "site"

    print("[build_site] Would assemble site")
    print(f"  Templates: {templates_dir}")
    print(f"  Output: {site_dir}")
    print(f"  Preview: {args.preview}")


if __name__ == "__main__":
    main()
