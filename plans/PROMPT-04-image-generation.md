# Prompt 04 — Image Generation

Use this prompt when you're ready to connect real image generation (replacing the placeholder SVGs).

> **NOTE:** We already have a working image generation system in `../esl`. Reuse the
> proven patterns from there rather than building from scratch. Key files to study:
> - `../esl/esl/image_gen.py` — Replicate API integration, background removal
> - `../esl/esl/image_lookup.py` — Image caching & discovery system
> - `../esl/esl/image_resolver.py` — Image resolution with 3-tier fallback

---

## Prompt

Read `PROJECT.md` for full context. Now implement the real image generation in `build/generate_images.py`.

**Before you start**, study the working image generation in `../esl/esl/image_gen.py` and `../esl/esl/image_lookup.py`. Reuse the same Replicate API approach, background removal logic, and caching patterns. Adapt them for this project's needs.

### Image Style

All images must share a consistent visual style. This is the most important thing — the cards should feel like they come from the same illustrated book.

**Style brief:**
- Hand-drawn illustration style, like a vintage natural history atlas or a beloved children's encyclopedia
- Black ink outlines/contours, confident but not rigid
- Soft watercolor fills — warm, saturated but not garish
- Clean white or very light background (so it works on the white card)
- Single subject, centered, with a bit of breathing room
- Charming and warm, not clinical or cartoonish
- No text in the image whatsoever
- Suitable for adults with disabilities — not childish, but friendly and clear

**Prompt template:**
```
A hand-drawn illustration in the style of a vintage natural history atlas.
Black ink contours with soft watercolor fills in warm, natural colors.
Clean white background. Single centered subject. No text.
Charming and clear, suitable for an educational card.
Subject: a [ENGLISH_WORD]
```

For abstract concepts (colors, actions), adapt the subject:
- Colors: "a watercolor swatch of [COLOR]" or "a [COLOR] butterfly"
- Actions: "a person [DOING THE ACTION]" in the same style
- Household items: straightforward illustration

### Implementation — Reuse from ESL

The ESL project (`../esl`) already has a working implementation. Adapt it:

**From `../esl/esl/image_gen.py`:**
- Replicate API integration using `cuuupid/sdxl-lineart` model
- API config: 512×512, 20 inference steps, guidance scale 9, K_EULER scheduler
- Background removal via flood-fill cleaning (brightness threshold 240px)
- Generates `_cleaned` versions alongside originals
- Read `REPLICATE_API_TOKEN` from env var

**From `../esl/esl/image_lookup.py`:**
- Image caching in a dedicated directory (ESL uses `img_words/`)
- Filename convention: `{word}_{timestamp}_{prompt_hash}.png`
- Skip-existing logic for batch generation
- Prefers cleaned versions automatically

Adapt `generate_images.py` to:

1. Use `REPLICATE_API_TOKEN` env var (same as ESL — one token for both projects)
2. For each word:
   - Check cache first (skip if exists, unless `--force`)
   - Construct the prompt using the template above
   - Call Replicate API with SDXL-lineart model (same config as ESL)
   - Run background removal (port the flood-fill cleaning from ESL)
   - Save as PNG, then convert to WebP using Pillow (`quality=85`)
   - Target size: 512×512px
3. Add a `--review` mode that generates images and opens them in a grid (simple HTML page) for manual review before committing
4. Add a `--regenerate cat,dog` flag to regenerate specific words only
5. Save the raw API prompt used for each image in a sidecar file (`{id}.prompt.txt`) for reproducibility

### Fallback

Use the same 3-tier fallback as ESL (`../esl/esl/image_resolver.py`):
1. Check for pre-made/cached images
2. Attempt generation via Replicate API
3. Fall back to placeholder SVG

If the API is unavailable or fails:
- Log the error clearly
- Keep the placeholder SVG
- Mark the word as "needs image" in the build report

### Image Post-Processing

After generation (reuse ESL's approach):
- Run background removal (flood-fill cleaning from `image_gen.py`)
- Convert to WebP (Pillow)
- Ensure dimensions are exactly 512×512 (crop/pad if needed)
- Optimize file size (target: under 100KB per image)
- Generate a tiny blurred placeholder (32×32, base64) for lazy loading in the frontend
