"""Generate illustrations for each word in a week.

Supports two modes:
- placeholder (default): generates simple SVG placeholders converted to WebP
- api: uses Replicate API with SDXL-lineart model (same as ../esl)
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent

STYLE_PREFIX = """A lovely hand-drawn illustration in the style of a vintage natural history atlas.
Black ink contours with soft, warm watercolor fills. Clean white background.
Simple, charming, suitable for educational materials for children.
Single subject, centered, no text in the image."""

# Soft pastel colors for placeholder backgrounds
PASTEL_COLORS = [
    "#FFE0E0",  # light pink
    "#E0F0FF",  # light blue
    "#E0FFE0",  # light green
    "#FFF0E0",  # light peach
    "#F0E0FF",  # light lavender
    "#FFFFE0",  # light yellow
    "#E0FFFF",  # light cyan
    "#FFE0F0",  # light rose
    "#F0FFE0",  # light lime
    "#E0E0FF",  # light periwinkle
]

IMAGE_SIZE = 512


def pastel_color_for_word(word_id: str) -> str:
    """Get a consistent pastel color based on the word id hash."""
    h = int(hashlib.md5(word_id.encode()).hexdigest(), 16)  # noqa: S324
    return PASTEL_COLORS[h % len(PASTEL_COLORS)]


def generate_placeholder_image(word: dict[str, str], output_path: Path) -> None:
    """Generate a soft pastel placeholder image with the word centered."""
    bg_color = pastel_color_for_word(word["id"])

    img = Image.new("RGB", (IMAGE_SIZE, IMAGE_SIZE), bg_color)
    draw = ImageDraw.Draw(img)

    # Try to use a reasonable font size
    display_text = word["english"]
    font_size = 48

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()

    # Get text bounding box and center it
    bbox = draw.textbbox((0, 0), display_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (IMAGE_SIZE - text_width) / 2
    y = (IMAGE_SIZE - text_height) / 2

    # Draw text with a slightly darker shade
    draw.text((x, y), display_text, fill="#555555", font=font)

    # Save as WebP
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), "WEBP", quality=85)


def generate_api_image(word: dict[str, str], output_path: Path) -> None:
    """Stub for Replicate API image generation (Phase 4)."""
    prompt = f"{STYLE_PREFIX}\n\nSubject: {word['english']}"
    print(f"    [API mode] Would generate image for '{word['english']}'")
    print(f"    Prompt: {prompt[:80]}...")
    print("    Model: cuuupid/sdxl-lineart (512x512, 20 steps, guidance 9, K_EULER)")
    print(f"    Output: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--week", required=True, help="Week ID (e.g. 2026-W13)")
    parser.add_argument("--force", action="store_true", help="Regenerate existing images")
    parser.add_argument(
        "--mode",
        choices=["placeholder", "api"],
        default="placeholder",
        help="Generation mode (default: placeholder)",
    )
    parser.add_argument("--regenerate", help="Regenerate specific words only (comma-separated)")
    args = parser.parse_args()

    # Read week JSON
    data_dir = PROJECT_ROOT / "site" / "data"
    week_path = data_dir / f"week-{args.week}.json"

    if not week_path.exists():
        print(f"  ERROR: Week data not found: {week_path}", file=sys.stderr)
        sys.exit(1)

    week_data = json.loads(week_path.read_text(encoding="utf-8"))
    words = week_data["words"]

    # Filter words if --regenerate is specified
    regenerate_ids: set[str] | None = None
    if args.regenerate:
        regenerate_ids = {s.strip() for s in args.regenerate.split(",")}

    # Output directory
    output_dir = data_dir / args.week
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[generate_images] Generating images for week {args.week}")
    print(f"  Mode: {args.mode}")
    print(f"  Output: {output_dir}")
    print(f"  Words: {len(words)}")

    generated = 0
    skipped = 0

    for word in words:
        # Skip if not in regenerate list
        if regenerate_ids is not None and word["id"] not in regenerate_ids:
            skipped += 1
            continue

        output_path = output_dir / word["image"]

        # Skip if already exists (unless --force)
        if output_path.exists() and not args.force:
            skipped += 1
            continue

        if args.mode == "placeholder":
            generate_placeholder_image(word, output_path)
            print(f"    {word['english']}: placeholder generated")
        else:
            generate_api_image(word, output_path)

        generated += 1

    print(f"  Done: {generated} images generated, {skipped} skipped")


if __name__ == "__main__":
    main()
