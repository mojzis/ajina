"""Parse a teacher's word list into structured JSON.

Reads a simple text file (one word pair per line: czech, english, pronunciation)
and produces a week JSON file + updates the index.
"""

import argparse
import re
import sys
from pathlib import Path

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
        "image": f"{word_id}.webp",
        "audio_cs": f"{word_id}_cs.mp3",
        "audio_en": f"{word_id}_en.mp3",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Path to word list file")
    parser.add_argument("--week", required=True, help="Week ID (e.g. 2026-W13)")
    parser.add_argument("--title", required=True, help="Czech title for the week")
    parser.add_argument("--title-en", required=True, help="English title for the week")
    args = parser.parse_args()

    # TODO: Implement in Phase 3
    print(f"[parse_words] Would parse {args.input}")
    print(f"  Week: {args.week}")
    print(f"  Title: {args.title} / {args.title_en}")

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"  ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    lines = input_path.read_text(encoding="utf-8").splitlines()
    words = [w for line in lines if (w := parse_line(line)) is not None]
    print(f"  Parsed {len(words)} words")

    for word in words:
        print(f"    {word['czech']} → {word['english']} [{word['pronunciation']}]")


if __name__ == "__main__":
    main()
