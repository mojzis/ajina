"""Parse a teacher's word list into structured JSON.

Reads a simple text file (one word pair per line: czech, english, pronunciation)
and produces a week JSON file + updates the index.
"""

import argparse
import json
import random
import re
import string
import sys
from datetime import date
from pathlib import Path
from typing import Any, cast

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def slugify(text: str) -> str:
    """Convert text to a URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def parse_line(line: str) -> dict[str, str] | None:
    """Parse a single line of the word list."""
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    parts = [p.strip() for p in line.split(",")]
    if len(parts) < 2:
        print(f"  Skipping malformed line: {line!r}", file=sys.stderr)
        return None

    czech = parts[0]
    english = parts[1]
    pronunciation = parts[2] if len(parts) >= 3 else ""
    word_id = slugify(english)

    return {
        "id": word_id,
        "czech": czech,
        "english": english,
        "pronunciation": pronunciation,
        "image": f"{word_id}-{''.join(random.choices(string.ascii_lowercase, k=6))}.webp",
        "audio_cs": f"{word_id}_cs.mp3",
        "audio_en": f"{word_id}_en.mp3",
    }


def deduplicate_words(words: list[dict[str, str]]) -> list[dict[str, str]]:
    """Remove duplicate words by id, keeping the first occurrence."""
    seen: set[str] = set()
    unique: list[dict[str, str]] = []
    for word in words:
        if word["id"] not in seen:
            seen.add(word["id"])
            unique.append(word)
        else:
            print(f"  Skipping duplicate: {word['english']!r}", file=sys.stderr)
    return unique


def update_index(data_dir: Path, week_id: str, title: str, title_en: str, word_count: int) -> None:
    """Update site/data/index.json with this week's entry."""
    index_path = data_dir / "index.json"

    if index_path.exists():
        index_data: dict[str, Any] = json.loads(index_path.read_text(encoding="utf-8"))
    else:
        index_data = {"current_week": "", "weeks": []}

    # Update or add week entry
    week_entry: dict[str, Any] = {
        "week_id": week_id,
        "title": title,
        "title_en": title_en,
        "published": date.today().isoformat(),
        "word_count": word_count,
    }

    # Replace existing entry or append
    weeks = cast(list[dict[str, Any]], index_data["weeks"])
    found = False
    for i, w in enumerate(weeks):
        if w["week_id"] == week_id:
            weeks[i] = week_entry
            found = True
            break
    if not found:
        weeks.insert(0, week_entry)

    # Set as current week
    index_data["current_week"] = week_id

    # Sort weeks by week_id descending
    weeks.sort(key=lambda w: w["week_id"], reverse=True)

    content = json.dumps(index_data, indent=2, ensure_ascii=False) + "\n"
    index_path.write_text(content, encoding="utf-8")
    print(f"  Updated index: {index_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Path to word list file")
    parser.add_argument("--week", required=True, help="Week ID (e.g. 2026-W13)")
    parser.add_argument("--title", required=True, help="Czech title for the week")
    parser.add_argument("--title-en", required=True, help="English title for the week")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"  ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    print(f"[parse_words] Parsing {input_path}")
    print(f"  Week: {args.week}")
    print(f"  Title: {args.title} / {args.title_en}")

    lines = input_path.read_text(encoding="utf-8").splitlines()
    words = [w for line in lines if (w := parse_line(line)) is not None]
    words = deduplicate_words(words)

    print(f"  Parsed {len(words)} words:")
    for word in words:
        pron = f" [{word['pronunciation']}]" if word["pronunciation"] else ""
        print(f"    {word['czech']} -> {word['english']}{pron}")

    # Write week JSON
    data_dir = PROJECT_ROOT / "site" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    week_data = {
        "week_id": args.week,
        "title": args.title,
        "title_en": args.title_en,
        "published": date.today().isoformat(),
        "words": words,
    }

    week_path = data_dir / f"week-{args.week}.json"
    content = json.dumps(week_data, indent=2, ensure_ascii=False) + "\n"
    week_path.write_text(content, encoding="utf-8")
    print(f"  Wrote week data: {week_path}")

    # Update index
    update_index(data_dir, args.week, args.title, args.title_en, len(words))


if __name__ == "__main__":
    main()
