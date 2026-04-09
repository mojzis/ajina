"""Generate a preview page comparing prompt variants for image generation.

For each word in a week, generates images with all prompt variants and
produces an HTML comparison page at site/preview/index.html.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

from dotenv import load_dotenv
from generate_images import (
    DEFAULT_VARIANT,
    PROMPT_VARIANTS,
    generate_api_image,
)
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent

THUMB_SIZE = 192
THUMB_SUFFIX = ".thumb.webp"

load_dotenv(PROJECT_ROOT / ".env")


def generate_preview(week_id: str, *, force: bool = False) -> Path:
    """Generate images for all variants and build comparison HTML."""
    data_dir = PROJECT_ROOT / "site" / "data"
    week_path = data_dir / f"week-{week_id}.json"

    if not week_path.exists():
        print(f"ERROR: Week data not found: {week_path}", file=sys.stderr)
        sys.exit(1)

    week_data = json.loads(week_path.read_text(encoding="utf-8"))
    words: list[dict[str, str]] = week_data["words"]
    variants = list(PROMPT_VARIANTS.keys())

    preview_dir = PROJECT_ROOT / "site" / "preview"
    preview_dir.mkdir(parents=True, exist_ok=True)

    # Generate images for each variant
    for variant in variants:
        variant_dir = preview_dir / variant
        variant_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n--- Variant: {variant} ---")
        for word in words:
            img_name = word["image"]
            output_path = variant_dir / img_name

            if output_path.exists() and not force:
                print(f"  {word['english']} ({variant}): cached")
                continue

            success = generate_api_image(word, output_path, force=force, variant=variant)
            if not success:
                print(
                    f"  ABORT: '{word['english']}' ({variant}) failed — "
                    "likely safety filter or API error. Stopping preview run.",
                    file=sys.stderr,
                )
                sys.exit(2)
            _make_thumbnail(output_path)

    # Ensure thumbnails exist for any cached images too
    for variant in variants:
        for word in words:
            img_path = preview_dir / variant / word["image"]
            if img_path.exists():
                _make_thumbnail(img_path)

    # Build comparison HTML
    return _build_comparison_html(words, variants, preview_dir, week_id)


def _thumbnail_path(img_path: Path) -> Path:
    """Sibling thumbnail path for a given full-size image."""
    return img_path.with_name(img_path.stem + THUMB_SUFFIX)


def _make_thumbnail(img_path: Path) -> None:
    """Generate a small WebP thumbnail next to the full image (idempotent)."""
    if not img_path.exists() or img_path.name.endswith(THUMB_SUFFIX):
        return
    thumb_path = _thumbnail_path(img_path)
    if thumb_path.exists() and thumb_path.stat().st_mtime >= img_path.stat().st_mtime:
        return
    img = Image.open(img_path).convert("RGB")
    img.thumbnail((THUMB_SIZE, THUMB_SIZE))
    thumb_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(thumb_path), "WEBP", quality=70)


def _embed_image(img_path: Path) -> str:
    """Return a data URI for an image (prefers thumbnail), empty if missing."""
    thumb = _thumbnail_path(img_path)
    chosen = thumb if thumb.exists() else img_path
    if not chosen.exists():
        return ""
    img_data = chosen.read_bytes()
    b64 = base64.b64encode(img_data).decode("ascii")
    return f"data:image/webp;base64,{b64}"


def _build_comparison_html(
    words: list[dict[str, str]],
    variants: list[str],
    preview_dir: Path,
    week_id: str,
) -> Path:
    """Build the comparison HTML page."""
    variant_headers = "".join(
        f"<th>{v}{'  (current)' if v == DEFAULT_VARIANT else ''}</th>" for v in variants
    )

    rows: list[str] = []
    for word in words:
        cells: list[str] = []
        for variant in variants:
            img_path = preview_dir / variant / word["image"]
            src = _embed_image(img_path)

            prompt_path = img_path.with_suffix(".prompt.txt")
            prompt_text = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else "N/A"

            cells.append(f"""
            <td>
                <img src="{src}" alt="{word["english"]} - {variant}" width="256" height="256">
                <details><summary>Full prompt sent</summary><pre>{prompt_text}</pre></details>
            </td>""")

        scene = word.get("image_prompt", "")
        scene_html = f'<div class="scene"><em>scene:</em> {scene}</div>' if scene else ""

        rows.append(f"""
        <tr>
            <td class="word-label">
                <strong>{word["english"]}</strong><br>
                <small>{word["czech"]}</small>
                {scene_html}
            </td>
            {"".join(cells)}
        </tr>""")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Image Variant Preview - {week_id}</title>
<style>
body {{
    font-family: system-ui, -apple-system, sans-serif;
    padding: 2rem;
    background: #f8f9fa;
    color: #333;
}}
h1 {{ margin-bottom: 0.5rem; }}
.subtitle {{ color: #666; margin-bottom: 2rem; }}
table {{
    border-collapse: collapse;
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0,0,0,.08);
}}
th, td {{
    padding: 1rem;
    text-align: center;
    border: 1px solid #e9ecef;
}}
th {{
    background: #343a40;
    color: white;
    font-size: 1rem;
    font-weight: 600;
}}
td img {{
    border-radius: 8px;
    background: #f0f0f0;
    display: block;
    margin: 0 auto;
}}
.word-label {{
    font-size: 1.1rem;
    min-width: 180px;
    max-width: 240px;
    background: #f8f9fa;
    text-align: left;
    vertical-align: top;
}}
.scene {{
    margin-top: .5rem;
    font-size: .75rem;
    color: #555;
    line-height: 1.3;
}}
details {{ margin-top: .5rem; text-align: left; }}
pre {{
    font-size: .7rem;
    white-space: pre-wrap;
    background: #f5f5f5;
    padding: .5rem;
    border-radius: 4px;
    max-width: 240px;
}}
</style>
</head>
<body>
<h1>Image Variant Preview</h1>
<p class="subtitle">Week {week_id} &mdash; {len(words)} words &times; {len(variants)} variants</p>
<table>
<thead>
    <tr>
        <th>Word</th>
        {variant_headers}
    </tr>
</thead>
<tbody>
{"".join(rows)}
</tbody>
</table>
</body>
</html>"""

    html_path = preview_dir / "index.html"
    html_path.write_text(html, encoding="utf-8")
    print(f"\nPreview page: {html_path}")
    return html_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--week", required=True, help="Week ID (e.g. 2026-W13)")
    parser.add_argument("--force", action="store_true", help="Regenerate all images")
    args = parser.parse_args()

    generate_preview(args.week, force=args.force)


if __name__ == "__main__":
    main()
