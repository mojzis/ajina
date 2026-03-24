"""Generate illustrations for each word in a week.

Supports two modes:
- placeholder (default): generates simple pastel placeholder images as WebP
- api: uses Replicate API with Google Imagen 3 model

Also supports:
- --review: generates an HTML review page showing all images in a grid
- --regenerate: regenerate specific words only (comma-separated IDs)
- --force: regenerate all images even if cached
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")

PROMPT_VARIANTS: dict[str, str] = {
    "atlas": (
        "A hand-drawn illustration in the style of a vintage natural history atlas.\n"
        "Black ink contours with soft watercolor fills in warm, natural colors.\n"
        "Clean white background. Single centered subject. No text.\n"
        "Charming and clear, suitable for an educational card.\n"
        "Subject: a {word}"
    ),
    "kawaii": (
        "A single {word}, cute kawaii style illustration with bold black outlines.\n"
        "Bright vivid colors, simple shapes, cheerful expression.\n"
        "Solid white background, centered, no text, no extra objects.\n"
        "Children's educational flashcard style."
    ),
    "flat": (
        "A single {word}, modern flat vector illustration.\n"
        "Bold geometric shapes, bright saturated colors, clean edges.\n"
        "Solid white background, centered composition, one subject only.\n"
        "No text, no shadows, no gradients. Educational poster style."
    ),
}

DEFAULT_VARIANT = "atlas"

# Replicate model config
REPLICATE_MODEL = "google/imagen-3"
IMAGE_SIZE = 512

# Soft pastel colors for placeholder backgrounds
PASTEL_COLORS = [
    "#FFE0E0",
    "#E0F0FF",
    "#E0FFE0",
    "#FFF0E0",
    "#F0E0FF",
    "#FFFFE0",
    "#E0FFFF",
    "#FFE0F0",
    "#F0FFE0",
    "#E0E0FF",
]


def pastel_color_for_word(word_id: str) -> str:
    """Get a consistent pastel color based on the word id hash."""
    h = int(hashlib.md5(word_id.encode()).hexdigest(), 16)  # noqa: S324
    return PASTEL_COLORS[h % len(PASTEL_COLORS)]


def generate_placeholder_image(word: dict[str, str], output_path: Path) -> None:
    """Generate a soft pastel placeholder image with the word centered."""
    bg_color = pastel_color_for_word(word["id"])

    img = Image.new("RGB", (IMAGE_SIZE, IMAGE_SIZE), bg_color)
    draw = ImageDraw.Draw(img)

    display_text = word["english"]
    font_size = 48

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), display_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (IMAGE_SIZE - text_width) / 2
    y = (IMAGE_SIZE - text_height) / 2

    draw.text((x, y), display_text, fill="#555555", font=font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), "WEBP", quality=85)


def build_prompt(english_word: str, variant: str = DEFAULT_VARIANT) -> str:
    """Build the image generation prompt for a word."""
    template = PROMPT_VARIANTS[variant]
    return template.format(word=english_word)


def ensure_dimensions(img: Image.Image, size: int = IMAGE_SIZE) -> Image.Image:
    """Ensure image is exactly size x size, cropping or padding as needed."""
    w, h = img.size
    if w == size and h == size:
        return img

    # Center-crop if larger, or pad with white if smaller
    result = Image.new("RGB", (size, size), (255, 255, 255))
    paste_x = (size - w) // 2
    paste_y = (size - h) // 2

    if w > size or h > size:
        # Crop from center
        left = max(0, (w - size) // 2)
        top = max(0, (h - size) // 2)
        img = img.crop((left, top, left + min(w, size), top + min(h, size)))
        paste_x = max(0, (size - img.size[0]) // 2)
        paste_y = max(0, (size - img.size[1]) // 2)

    result.paste(img, (paste_x, paste_y))
    return result


def generate_api_image(
    word: dict[str, str],
    output_path: Path,
    *,
    force: bool = False,
    variant: str = DEFAULT_VARIANT,
) -> bool:
    """Generate image via Replicate API.

    Returns True if image was generated, False if failed (placeholder will be used).
    """
    import replicate as replicate_sdk

    token = os.environ.get("REPLICATE_API_TOKEN", "")
    if not token:
        print("    ERROR: REPLICATE_API_TOKEN env var not set", file=sys.stderr)
        return False

    prompt = build_prompt(word["english"], variant=variant)

    # Save prompt sidecar
    prompt_path = output_path.with_suffix(".prompt.txt")
    prompt_path.write_text(prompt, encoding="utf-8")

    try:
        print(f"    Calling Replicate API for '{word['english']}'...")
        output = replicate_sdk.run(
            REPLICATE_MODEL,
            input={
                "prompt": prompt,
                "aspect_ratio": "1:1",
                "output_format": "png",
                "safety_filter_level": "block_medium_and_above",
            },
        )

        # Imagen 3 returns a single FileOutput object
        raw_bytes = output.read()
        img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")

        # Background removal disabled — the lineart model already produces
        # clean backgrounds and removal was degrading image quality.

        # Ensure dimensions
        img = ensure_dimensions(img)

        # Save as WebP
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(output_path), "WEBP", quality=85)

        file_size = output_path.stat().st_size
        print(f"    Saved: {output_path.name} ({file_size // 1024}KB)")

        if file_size > 100 * 1024:
            # Try lower quality if too large
            img.save(str(output_path), "WEBP", quality=70)
            file_size = output_path.stat().st_size
            print(f"    Re-saved at q70: {file_size // 1024}KB")

    except Exception as e:
        print(f"    ERROR generating '{word['english']}': {e}", file=sys.stderr)
        return False

    return True


def generate_placeholder_svg_fallback(word: dict[str, str], output_path: Path) -> None:
    """Generate a placeholder when API fails — uses the pastel placeholder."""
    generate_placeholder_image(word, output_path)
    print(f"    Fallback: placeholder for '{word['english']}'")


def generate_review_html(words: list[dict[str, str]], output_dir: Path, week_id: str) -> Path:
    """Generate an HTML review page showing all images in a grid."""
    html_path = output_dir / "review.html"

    rows: list[str] = []
    for word in words:
        img_path = output_dir / word["image"]
        if img_path.exists():
            # Embed as base64
            img_data = img_path.read_bytes()
            b64 = base64.b64encode(img_data).decode("ascii")
            src = f"data:image/webp;base64,{b64}"
        else:
            src = ""

        prompt_path = img_path.with_suffix(".prompt.txt")
        prompt_text = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else "N/A"

        rows.append(f"""
        <div class="card">
            <img src="{src}" alt="{word["english"]}" width="256" height="256"
                 style="background:#f0f0f0;">
            <div class="label">
                <strong>{word["english"]}</strong><br>
                <small>{word["czech"]}</small>
            </div>
            <details><summary>Prompt</summary><pre>{prompt_text}</pre></details>
        </div>""")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Image Review - {week_id}</title>
<style>
body {{ font-family: sans-serif; padding: 2rem; }}
h1 {{ color: #333; }}
.grid {{
  display: grid; gap: 1.5rem;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
}}
.card {{
  background: white; border-radius: 12px;
  padding: 1rem; text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,.1);
}}
.card img {{ border-radius: 8px; }}
.label {{ margin-top: .5rem; }}
details {{ margin-top: .5rem; text-align: left; }}
pre {{
  font-size: .75rem; white-space: pre-wrap;
  background: #f5f5f5; padding: .5rem;
  border-radius: 4px;
}}
</style>
</head>
<body>
<h1>Image Review: {week_id}</h1>
<p>{len(words)} words</p>
<div class="grid">
{"".join(rows)}
</div>
</body>
</html>"""

    html_path.write_text(html, encoding="utf-8")
    return html_path


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
    parser.add_argument("--regenerate", help="Regenerate specific words only (comma-separated IDs)")
    parser.add_argument(
        "--review", action="store_true", help="Generate HTML review page after images"
    )
    parser.add_argument(
        "--variant",
        choices=list(PROMPT_VARIANTS.keys()),
        default=DEFAULT_VARIANT,
        help=f"Prompt variant (default: {DEFAULT_VARIANT})",
    )
    args = parser.parse_args()

    # Read week JSON
    data_dir = PROJECT_ROOT / "site" / "data"
    week_path = data_dir / f"week-{args.week}.json"

    if not week_path.exists():
        print(f"  ERROR: Week data not found: {week_path}", file=sys.stderr)
        sys.exit(1)

    week_data = json.loads(week_path.read_text(encoding="utf-8"))
    words: list[dict[str, str]] = week_data["words"]

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
    failed: list[str] = []

    for word in words:
        # Skip if not in regenerate list
        if regenerate_ids is not None and word["id"] not in regenerate_ids:
            skipped += 1
            continue

        output_path = output_dir / word["image"]

        # Skip if already exists (unless --force or --regenerate targets it)
        if output_path.exists() and not args.force and regenerate_ids is None:
            skipped += 1
            continue

        if args.mode == "placeholder":
            generate_placeholder_image(word, output_path)
            print(f"    {word['english']}: placeholder generated")
            generated += 1
        else:
            # 3-tier fallback: cache -> API -> placeholder
            if output_path.exists() and not args.force and regenerate_ids is None:
                skipped += 1
                continue

            success = generate_api_image(word, output_path, force=args.force, variant=args.variant)
            if success:
                generated += 1
            else:
                # Fallback to placeholder
                generate_placeholder_svg_fallback(word, output_path)
                failed.append(word["id"])
                generated += 1

    print(f"  Done: {generated} generated, {skipped} skipped")
    if failed:
        print(f"  WARNING: {len(failed)} words need real images: {', '.join(failed)}")

    # Generate review page if requested
    if args.review:
        review_path = generate_review_html(words, output_dir, args.week)
        print(f"  Review page: {review_path}")


if __name__ == "__main__":
    main()
